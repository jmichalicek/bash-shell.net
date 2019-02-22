from django.utils import timezone
from django.db.models import QuerySet

from wagtail.core.models import Page, PageManager, PageQuerySet


class PublishedPostQuerySet(QuerySet):
    """
    Returns posts which are published
    """
    def published(self, *args, **kwargs):
        return self.filter(is_published=True, published_date__isnull=False, published_date__lte=timezone.now())
