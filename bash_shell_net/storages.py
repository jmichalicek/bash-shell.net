from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.staticfiles.storage import CachedFilesMixin


class StaticStorage(CachedFilesMixin, S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    file_overwrite_file = True
    max_post_process_passes = 15  # ckeditor is not playing nicely with the default 5, set it high
    manifest_strict = False  #hopefully stop things from blowing up if the file is missing.  eventually remove these two


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
