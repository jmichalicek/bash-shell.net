from __future__ import unicode_literals, absolute_import, division

from django.utils import timezone

from datetime import timedelta
from factory.django import DjangoModelFactory


class UnpublishedPostFactory(DjangoModelFactory):
    is_published = False
    published_data = None
    title = factory.Sequence(lambda n: u'Unpublished Post %03d' % n)
    content = factory.Sequence(lambda n: u'Content of unpublished post %03d' % n)

    class Meta:
        model = 'blog.models.Post'

class PublishedPostFactory(UnpublishedPostFactory):
    is_published = True
    title = factory.Sequence(lambda n: u'Published post %03d' % n)
    content = factory.Sequence(lambda n: u'Content of post %03d' % n)

    class Meta:
        model = 'blog.models.Post'
