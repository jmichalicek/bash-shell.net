from datetime import timedelta

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory


class UnpublishedPostFactory(DjangoModelFactory):
    is_published = False
    published_date = None
    title = factory.Sequence(lambda n: u'Unpublished Post %03d' % n)
    content = factory.Sequence(lambda n: u'Content of unpublished post %03d' % n)

    class Meta:
        model = 'blog.Post'


class PublishedPostFactory(UnpublishedPostFactory):
    is_published = True
    title = factory.Sequence(lambda n: u'Published post %03d' % n)
    content = factory.Sequence(lambda n: u'Content of post %03d' % n)
    # ensure published_date is in the past
    published_date = factory.LazyAttribute(lambda n: timezone.now() - timedelta(minutes=1))

    class Meta:
        model = 'blog.Post'
