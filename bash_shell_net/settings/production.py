import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # I am being lazy

CACHES = {
    # 'default': {'BACKEND': 'redis_cache.RedisCache', 'LOCATION': '%s:6379' % REDIS_HOST, 'OPTIONS': {'DB': 2,},},
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://%s:6379' % REDIS_HOST,
        'OPTIONS': {'DB': 2,},
    },
}

AWS_STORAGE_BUCKET_NAME = 'bash-shell-net'
# STATICFILES_LOCATION = 'static'  # this is an s3/boto thing and shouldn't be needed now
# STATICFILES_STORAGE = 'bash_shell_net.storages.StaticStorage'
MEDIAFILES_LOCATION = 'uploads'
DEFAULT_FILE_STORAGE = 'bash_shell_net.storages.MediaStorage'

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# TODO: can probably just move this to settings/base.py
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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
    'root': {'level': 'WARN', 'handlers': ['console'],},
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
    'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'json_formatter'}},
    'loggers': {
        'django': {'level': 'INFO', 'handlers': ['console'], 'propagate': False,},
        'django.request': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False,},
    },
    # might want django.request logger at DEBUG level
}
