"""
A test runner with slow tests logged. Originally from https://hakibenita.com/timing-tests-in-python-for-fun-and-profit
and updated to work with Django's DiscoverRunner
"""
import time
import unittest
from unittest.runner import TextTestResult

from django.test.runner import DiscoverRunner
import logging


class TimeLoggingTestResult(TextTestResult):

    test_timings: list[float]
    _test_started_at: float

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_timings = []

    def startTest(self, test):
        self._test_started_at = time.time()
        super().startTest(test)

    def addSuccess(self, test):
        elapsed = time.time() - self._test_started_at
        name = self.getDescription(test)
        self.test_timings.append((name, elapsed))
        super().addSuccess(test)

    def getTestTimings(self) -> list[float]:
        return self.test_timings


class TimeLoggingTestRunner(unittest.TextTestRunner):
    def __init__(self, slow_test_threshold=0.3, *args, **kwargs):
        self.slow_test_threshold = slow_test_threshold
        # Could also override get_resultclass() in TimedLoggingDiscoverRunner to return
        # TimeLoggingTestResult
        kwargs.update({'resultclass': TimeLoggingTestResult})
        return super().__init__(*args, **kwargs)

    def run(self, test):
        result = super().run(test)

        self.stream.writeln(f"\nSlow Tests (>{self.slow_test_threshold:.03}s):")
        for name, elapsed in result.getTestTimings():
            if elapsed > self.slow_test_threshold:
                self.stream.writeln(f"({elapsed:.03}s) {name}")

        return result


class TimedLoggingDiscoverRunner(DiscoverRunner):
    test_runner = TimeLoggingTestRunner

    @classmethod
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--enable-logging",
            action="store_true",
            default=False,
            help="Enables the python logger",
        )

    def __init__(self, enable_logging: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_logging = enable_logging

    def setup_databases(self, **kwargs):
        # Force to always delete the database if it exists
        interactive = self.interactive
        self.interactive = False
        try:
            return super().setup_databases(**kwargs)
        finally:
            self.interactive = interactive

    def run_tests(self, *args, **kwargs):
        if not self.enable_logging:
            logging.disable(level=logging.CRITICAL)
        return super().run_tests(*args, **kwargs)
