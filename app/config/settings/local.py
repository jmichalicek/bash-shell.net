from .base import *
import structlog

WAGTAIL_SITE_NAME = 'bash-shell.net development'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache',}}
DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

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
    'root': {'level': 'WARN', 'handlers': ['console_key_value'],},
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
        'django': {'level': 'INFO', 'handlers': ['console_key_value'], 'propagate': False,},
        'django.request': {'handlers': ['console_key_value'], 'level': 'DEBUG', 'propagate': False,},
        'django.server': {'handlers': ['console_key_value'], 'level': 'DEBUG', 'propagate': False,},
        # Log SQL queries - noisy, but sometimes useful
        # 'django.db.backends': {'handlers': ['console_plain'], 'level': 'DEBUG', 'propagate': False,},
    },
}
