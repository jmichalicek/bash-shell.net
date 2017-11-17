from django.test import TestCase
from django.utils.text import slugify
from django.core.urlresolvers import reverse

from .factories import PublishedPostFactory
from .models import Tag


class TagTests(TestCase):
    """Test the Tag model"""

    def test_save(self):
        """
        Test that save sets slug
        """

        tag = Tag(name='A Tag')
        tag.save()
        self.assertEqual('a-tag', tag.slug)


class PostTests(TestCase):
    """
    Test the Post model
    """

    @classmethod
    def setUpTestData(cls):
        cls.post = PublishedPostFactory()

    def setUp(self):
        self.post.refresh_from_db()

    def test_str(self):
        self.assertEqual(self.post.title, self.post.__str__())

    def test_get_absolute_url_when_published(self):
        self.assertEqual(self.post.get_absolute_url(), reverse('blog_post_detail', args=[self.post.slug]))

    def test_get_absolute_url_when_not_published(self):
        """
        Unpublished posts should return the preview url
        """
        self.post.is_published = False
        self.assertEqual(self.post.get_absolute_url(), reverse('blog_post_preview', args=[self.post.slug]))

    def test_save(self):
        """
        Test the overridden save() sets correct slug
        """
        self.post.slug = ''
        self.post.save()
        self.assertEqual(slugify(self.post.title), self.post.slug)
