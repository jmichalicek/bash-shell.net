import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

AWS_STORAGE_BUCKET_NAME = 'bash-shell-net'
# STATICFILES_LOCATION = 'static'  # this is an s3/boto thing and shouldn't be needed now
# STATICFILES_STORAGE = 'bash_shell_net.storages.StaticStorage'
MEDIAFILES_LOCATION = 'uploads'
DEFAULT_FILE_STORAGE = 'config.storages.MediaStorage'


sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', ''),
    integrations=[DjangoIntegration()],
    # Since I have no traffic, this might be really low
    traces_sample_rate=0.2,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)
