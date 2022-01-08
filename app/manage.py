#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    # Coverage related stuff from https://adamj.eu/tech/2019/04/30/getting-a-django-application-to-100-percent-coverage/
    try:
        command = sys.argv[1]
    except IndexError:
        command = "help"
    running_tests = command == 'test'

    if running_tests:
        os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.test"
        from coverage import Coverage

        cov = Coverage()
        cov.erase()
        cov.start()
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

    if running_tests:
        cov.stop()
        cov.combine()
        cov.save()
        covered = cov.report()
        cov.erase()
        # Keep bumping this up as I add more tests
        print('Actual coverage percent:', covered)
        if covered < 75.5:  # Keep this up to date with actual coverage as it increases
            print('Test coverage below minimum. Failure.')
            sys.exit(1)
