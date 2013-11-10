from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test.client import Client

import markdown

from models import *

TEST_USER = 'test_user'
TEST_PASSWORD = 'test_password'
TEST_EMAIL = 'none@example.com'

class CategoryTests(TestCase):
    """Test the Category model"""

    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def tearDown(self):
        self.category.delete()


class CategoryUnicodeTests(CategoryTests):
    """Test the __unicode__() method of the Category class"""

    def test_unicode(self):
        """Test the __unicode__() method ouptut"""

        self.assertEqual(self.category.name, self.category.__unicode__())

class PostTests(TestCase):
    """Test the Post model"""
    fixtures = ['test_postmodeltests']

    def setUp(self):
        self.post = Post.objects.get(id=1)

class PostUnicodeTests(PostTests):
    """Test the __unicode__() method of the Post class"""

    def test_unicode(self):
        self.assertEqual(self.post.title, self.post.__unicode__())

class PostGetAbsoluteUrlTests(PostTests):
    """Test the get_absolute_url() method of the Post class"""

    def test_get_absolute_url(self):
        year = self.post.created_date.strftime('%Y')
        month = self.post.created_date.strftime('%b').lower()
        day = self.post.created_date.strftime('%d')

        self.assertEqual(self.post.get_absolute_url(), reverse('bsblog_full_post_url',
                                                               args=[year, month, day, self.post.slug]))
class PostSaveTests(PostTests):
    """Test the save() method of the Post class"""

    def test_markdown(self):
        """Test the overridden save() method converts the text_markdown field and saves in text_html"""
        self.post.text_html = ''
        self.post.text_markdown = '''**test**'''
        self.post.save()
        self.assertEqual(self.post.text_html,
                         markdown.markdown(self.post.text_markdown, safe_mode=False))


class UserProfileTests(TestCase):
    """Test the UserProfile model"""

    fixtures = ['test_userprofiletests']

    def setUp(self):
        self.user_profile = UserProfile.objects.get(id=1)


class UserProfileUnicodeTests(UserProfileTests):
    """Test the __unicode__() method of the UserProfile class"""

    def test_unicode(self):
        self.assertEqual(self.user_profile.user.username, self.user_profile.__unicode__())


class ArchiveViewTests(TestCase):
    """Test the archive view"""

    fixtures = ['test_archiveviewtests']

    def setUp(self):
        self.client = Client()
        self.post_2012 = Post.objects.get(id=1)
        self.post_2011 = Post.objects.get(id=2)

    def test_get_response_code(self):
        """Make sure we get a 200 response code"""
        response = self.client.get(reverse('bsblog_archive'))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('bsblog_archive'))
        self.assertEqual(response.templates[0].name, 'bsblog/archive.html')
        
    def test_no_args(self):
        response = self.client.get(reverse('bsblog_archive'))
        posts = response.context['post_list']
        self.assertEqual(2, len(posts))
        self.assertTrue(self.post_2012 in posts)
        self.assertTrue(self.post_2011 in posts)

class IndexViewTests(TestCase):
    """Test the index view"""

    fixtures = ['test_indexviewtests']

    def setUp(self):
        self.published_post = Post.objects.get(id=1)
        self.unpublished_post = Post.objects.get(id=2)

    def test_get_response_code(self):
        """Make sure we get a 200 response code"""
        response = self.client.get(reverse('bsblog_main'))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        response = self.client.get(reverse('bsblog_main'))
        self.assertEqual(response.templates[0].name, 'bsblog/index.html')

    def test_empty_page(self):
        """Verify that a 404 is returned when a page with no results is requested"""
        response = self.client.get(reverse('bsblog_main', args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_context_post_list(self):
        """Make sure our posts are in the post_list item in the context"""
        response = self.client.get(reverse('bsblog_main'))
        self.assertTrue('post_list' in response.context)
        self.assertTrue(self.published_post in response.context['post_list'])

    def test_unpublished_post(self):
        """Make sure unpublished posts are NOT in the post_list"""
        response = self.client.get(reverse('bsblog_main'))
        self.assertFalse(self.unpublished_post in response.context['post_list'])


class ItemViewTests(TestCase):
    """Test the item view"""

    fixtures = ['test_itemviewtests']

    def setUp(self):
        self.post = Post.objects.get(id=1)

    def test_get_response_code(self):
        """Make sure we get a 200 response code"""
        year = self.post.created_date.strftime('%Y')
        month = self.post.created_date.strftime('%b').lower()
        day = self.post.created_date.strftime('%d')

        response = self.client.get(reverse('bsblog_full_post_url', args=[year, month, day,
                                                                         self.post.slug]))
        self.assertEqual(response.status_code, 200)

    def test_template(self):
        year = self.post.created_date.strftime('%Y')
        month = self.post.created_date.strftime('%b').lower()
        day = self.post.created_date.strftime('%d')

        response = self.client.get(reverse('bsblog_full_post_url', args=[year, month, day,
                                                                         self.post.slug]))

        self.assertEqual(response.templates[0].name, 'bsblog/blog_post.html')

    def test_context_post(self):
        year = self.post.created_date.strftime('%Y')
        month = self.post.created_date.strftime('%b').lower()
        day = self.post.created_date.strftime('%d')

        response = self.client.get(reverse('bsblog_full_post_url', args=[year, month, day,
                                                                         self.post.slug]))

        self.assertTrue('post' in response.context)
        self.assertEqual(response.context['post'], self.post)

        
