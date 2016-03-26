from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse

from .factories import *
from .models import *

TEST_USER = 'test_user'
TEST_PASSWORD = 'test_password'
TEST_EMAIL = 'none@example.com'

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

    def setUp(self):
        # move this to setUpTestData after django upgrade
        self.post = PublishedPostFactory()

    def test_unicode(self):
        self.assertEqual(self.post.title, self.post.__unicode__())

    def test_get_absolute_url(self):
        self.assertEqual(self.post.get_absolute_url(), reverse('blog_post_detail',
                                                               args=[self.post.slug]))
    def test_save(self):
        """
        Test the overridden save() sets correct slug
        """
        self.post.slug = ''
        self.post.save()
        self.assertEqual(slugify(self.post.title), self.post.slug)


class PostListViewTests(TestCase):
    """Test the index view"""

    URL_NAME = 'blog_post_list'

    def setUp(self):
        # move this to setUpTestData after django upgrade
        self.published_post = PublishedPostFactory()
        self.unpublished_post = UnpublishedPostFactory()

    def test_get(self):
        """Make sure we get a 200 response code"""
        response = self.client.get(reverse(self.URL_NAME))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'blog/post_list.html')
        self.assertTrue('post_list' in response.context)
        self.assertTrue(self.published_post in response.context['post_list'])
        self.assertFalse(self.unpublished_post in response.context['post_list'])

    def test_empty_page(self):
        """Verify that a 404 is returned when a page with no results is requested"""
        response = self.client.get(reverse(self.URL_NAME), {'page': 2})
        self.assertEqual(response.status_code, 404)


class PostDetailViewTests(TestCase):
    """Test the item view"""

    URL_NAME = 'blog_post_detail'

    def setUp(self):
        # move this to setUpTestData after django upgrade
        self.post = PublishedPostFactory()
        self.unpublished_post = UnpublishedPostFactory()

    def test_get(self):
        """Make sure we get a 200 response code"""
        response = self.client.get(reverse(self.URL_NAME, args=[self.post.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'blog/post_detail.html')
        self.assertTrue('post' in response.context)
        self.assertTrue('tags' in response.context)
        self.assertEqual(response.context['post'], self.post)

    def test_get_unpublished(self):
        response = self.client.get(reverse(self.URL_NAME, args=[self.unpublished_post.slug]))
        self.assertEqual(response.status_code, 404)
