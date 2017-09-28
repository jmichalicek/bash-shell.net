from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.contrib.staticfiles.storage import CachedFilesMixin, ManifestFilesMixin


# TODO: Test this against a real s3 bucket to see if problems are django-storages, django,
# or digital ocean spaces minor differences from s3.
# Error is that no matter what the files need post-processed too many times for hashing, even
# with gzip turned off.
# I have fixed this before for s3 and django-storages seems to have the same fix now, so I fear
# the issue is DO spaces.
class StaticStorage(ManifestFilesMixin, S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    file_overwrite = True
    #max_post_process_passes = 15  # ckeditor is not playing nicely with the default 5, set it high
    #manifest_strict = False  #hopefully stop things from blowing up if the file is missing.  eventually remove these two


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = False
