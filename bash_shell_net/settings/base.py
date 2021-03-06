# Django settings for bsdev project.
import logging
import os
import sys

import dj_database_url
import structlog
from structlog_sentry import SentryJsonProcessor

# This checks that the first arg to `manage.py` is `test`
# The main use case is to turn off caching specifically for tests because it makes things unpredictable
TESTING = sys.argv[1:2] == ['test']

# the dir with manage.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFENSE_LEAGUE = True
AUTH_USER_MODEL = 'accounts.User'
DEBUG = True
ADMINS = (('Justin Michalicek', 'jmichalicek@gmail.com'),)
MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(PROJECT_ROOT, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# since I'm now doing collectstatic in the docker image build, allowing this setting to vary is not so good.
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(PROJECT_ROOT, 'static_collected'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = os.environ.get('STATIC_URL', '/static/')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Make this unique, and don't share it with anybody.
# it's probably a good idea to override this with the env variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '5@r3yfc1j@cyh*uya0w&lrx_eyjt((@^#k1%!r4$u)eus!9m6x')

# Ordering based on https://docs.djangoproject.com/en/3.1/ref/middleware/#middleware-ordering
# and http://whitenoise.evans.io/en/stable/django.html#enable-whitenoise
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Should this go higher in the list?
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'django_structlog.middlewares.RequestMiddleware',
)

ROOT_URLCONF = 'bash_shell_net.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'bash_shell_net.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.flatpages',
    'django.contrib.sitemaps',
    # Wagtail
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtail.contrib.routable_page',
    # Wagtail extra deps
    'modelcluster',
    'taggit',
    'wagtailfontawesome',
    # Health/monitoring
    'watchman',
    # My stuff
    'internetdefenseleague',
    'accounts',
    'blog',
    'projects',
    'base',
    'on_tap.apps.OnTapConfig',
)

COVERAGE_PATH_EXCLUDES = [r'.svn', r'.git', r'templates', r'static']

ALLOWED_HOSTS = ['*']

# CACHING AND STORAGE
REDIS_HOST = os.environ.get('REDIS_HOST', '')
DATABASES = {
    'default': dj_database_url.config(default='sqlite:////{0}'.format(os.path.join(PROJECT_ROOT, 'bs_net.sqlite'))),
}

CACHES = {
    # 'default': {'BACKEND': 'redis_cache.RedisCache', 'LOCATION': '%s:6379' % REDIS_HOST, 'OPTIONS': {'DB': 2,},},
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://%s:6379' % REDIS_HOST,
        'OPTIONS': {'DB': 2,},
    },
}

# S3/DO spaces settings
AWS_IS_GZIPPED = True
AWS_ACCESS_KEY_ID = os.environ.get('DO_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('DO_SECRET_ACCESS_KEY', '')
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=604800'}
# This needs correctly set to work with digital ocean
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'https://nyc3.digitaloceanspaces.com')
AWS_QUERYSTRING_AUTH = False
AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', None)
AWS_PRELOAD_METADATA = True
AWS_DEFAULT_ACL = 'public-read'

# markdown extensions
# Not using markdown anymore... not sure I need this. may still be using it in the projects pages, though.
MARKDOWN_EXTENSIONS = ['markdown.extensions.extra', 'markdown.extensions.toc', 'markdown.extensions.codehilite']

# wagtail settings
WAGTAIL_SITE_NAME = 'bash-shell.net'
TAGGIT_CASE_INSENSITIVE = True  # might avoid taggit anyway.  I do not care for it

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        SentryJsonProcessor(level=logging.ERROR),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
LOGGING = {
    'version': 1,
    # 'disable_existing_loggers': True,
    'disable_existing_loggers': False,
    'root': {'level': os.environ.get('LOG_LEVEL', 'INFO'), 'handlers': ['console_json'],},
    'formatters': {
        'verbose': {'format': '%(levelname)s %(asctime)s %(module)s ' '%(process)d %(thread)d %(message)s'},
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
        "plain_console": {"()": structlog.stdlib.ProcessorFormatter, "processor": structlog.dev.ConsoleRenderer(),},
        "key_value": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.KeyValueRenderer(key_order=['timestamp', 'level', 'event', 'logger']),
        },
    },
    'handlers': {
        'console_json': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'json_formatter'},
        'console_plain': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'plain_console'},
        'console_key_value': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'key_value'},
    },
    'loggers': {
        'django': {'level': os.environ.get('LOG_LEVEL', 'INFO'), 'handlers': ['console_json'], 'propagate': False,},
        # only when not manage.py runserver
        'django.request': {
            'handlers': ['console_json'],
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console_json'],
            'level': os.environ.get('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        # only happens with manage.py runserver
        'django.server': {'handlers': ['console_json'], 'level': 'DEBUG', 'propagate': False,},
        # Log SQL queries - noisy, but sometimes useful
        # 'django.db.backends': {'handlers': ['console_plain'], 'level': 'DEBUG', 'propagate': False,},
    },
    # might want django.request logger at DEBUG level
}

# python -c "import secrets; print(secrets.token_urlsafe())"
WATCHMAN_TOKENS = os.environ.get('WATCHMAN_TOKENS', None)
WATCHMAN_CHECKS = (
    'watchman.checks.caches',
    'watchman.checks.databases',
)

if TESTING:
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

