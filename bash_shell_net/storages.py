from django.conf import settings
from django.contrib.staticfiles.storage import CachedFilesMixin
from storages.backends.s3boto import S3BotoStorage


class StaticStorage(CachedFilesMixin, S3BotoStorage):
    location = settings.STATICFILES_LOCATION
    file_overwrite_file = True


class MediaStorage(S3BotoStorage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
