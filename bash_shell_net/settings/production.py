from .base import *

DEBUG = False
ALLOWED_HOSTS = ['bash-shell.net']

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '%s:6379' % REDIS_HOST,
        'OPTIONS': {
            'DB': 2,
            },
        },
    }

MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

AWS_STORAGE_BUCKET_NAME = 'bash-shell-net'
STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'bash_shell_net.storages.StaticStorage'
MEDIAFILES_LOCATION = 'uploads'
DEFAULT_FILE_STORAGE = 'bash_shell_net.storages.MediaStorage'
