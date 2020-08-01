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
