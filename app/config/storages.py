from django.conf import settings
from django.contrib.staticfiles.storage import ManifestFilesMixin

from storages.backends.s3boto3 import S3Boto3Storage


# Really should remove this, doubt I'll ever use it again.
# Leaving it here caused it to initialize in production even when not referenced
# which caused exceptions to be raised wit the STATICFILES_LOCATION setting removed
# class StaticStorage(ManifestFilesMixin, S3Boto3Storage):
#     location = settings.STATICFILES_LOCATION
#     file_overwrite = True


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
