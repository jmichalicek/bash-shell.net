from .local import *

# faster password hashing in tests.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# For django_coverage_plugin
TEMPLATES[0]['OPTIONS']['debug'] = True

WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
# The above should have made it so that the whitenoise stuff is not used in tests and I do not need
# to run collectstatic to run tests, but I seem to be missing something still.
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
