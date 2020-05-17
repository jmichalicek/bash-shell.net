from .base import *

INSTALLED_APPS += ('django_coverage',)
WAGTAIL_SITE_NAME = 'bash-shell.net development'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache',}}
