from .base import *

INSTALLED_APPS += ('django_coverage',)
WAGTAIL_SITE_NAME = 'bash-shell.net development'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache',}}

LOGGING = {
    'version': 1,
    # 'disable_existing_loggers': True,
    'disable_existing_loggers': False,
    'root': {'level': 'WARN', 'handlers': ['console'],},
    'formatters': {
        'verbose': {'format': '%(levelname)s %(asctime)s %(module)s ' '%(process)d %(thread)d %(message)s'},
    },
    'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'verbose'}},
    'loggers': {'django': {'level': 'INFO', 'handlers': ['console'], 'propagate': False,},},
}
