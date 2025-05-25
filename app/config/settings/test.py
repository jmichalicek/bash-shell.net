from .local import *  # noqa

# faster password hashing in tests.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# For django_coverage_plugin
TEMPLATES[0]["OPTIONS"]["debug"] = True  # type: ignore

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
# The above should have made it so that the whitenoise stuff is not used in tests and I do not need
# to run collectstatic to run tests, but I seem to be missing something still.

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    # the above WHITENOISE_* settings SHOULD keep whitenoise from blowing up running tests when
    # collectstatic has not been run, but it is not. so just turn off whitenoise for now
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {"silent": {"()": lambda: False}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "filters": ["silent"]},
    },
    "root": {
        "handlers": [],
        "level": "CRITICAL",
    },
}
