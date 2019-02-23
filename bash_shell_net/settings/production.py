import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # I am being lazy

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '%s:6379' % REDIS_HOST,
        'OPTIONS': {
            'DB': 2,
        },
    },
}

# MIDDLEWARE = (
#     'django.middleware.cache.UpdateCacheMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.cache.FetchFromCacheMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     # Uncomment the next line for simple clickjacking protection:
#     # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
# )

MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
)

AWS_STORAGE_BUCKET_NAME = 'bash-shell-net'
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'bash_shell_net.storages.StaticStorage'
MEDIAFILES_LOCATION = 'uploads'
DEFAULT_FILE_STORAGE = 'bash_shell_net.storages.MediaStorage'

RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', ''),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    # 'release': raven.fetch_git_sha(os.path.abspath(os.pardir)),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',  # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {
                'custom-tag': 'x'
            },
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
