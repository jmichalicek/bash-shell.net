import unittest

from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify

from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests

from ..factories import PublishedPostFactory
from ..models import Tag, BlogPage, BlogPageIndex


class TagTests(TestCase):
    """Test the Tag model"""

    # DEPRECATED
    @unittest.skip('Model is deprecated and unused')
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

    # DEPRECATED
    @classmethod
    def setUpTestData(cls):
        cls.post = PublishedPostFactory()

    def setUp(self):
        self.post.refresh_from_db()

    @unittest.skip('Model is deprecated and unused')
    def test_str(self):
        self.assertEqual(self.post.title, self.post.__str__())

    @unittest.skip('Model is deprecated and unused')
    def test_get_absolute_url_when_published(self):
        self.assertEqual(self.post.get_absolute_url(), reverse('blog_post_detail', args=[self.post.slug]))

    @unittest.skip('Model is deprecated and unused')
    def test_get_absolute_url_when_not_published(self):
        """
        Unpublished posts should return the preview url
        """
        self.post.is_published = False
        self.assertEqual(self.post.get_absolute_url(), reverse('blog_post_preview', args=[self.post.slug]))

    @unittest.skip('Model is deprecated and unused')
    def test_save(self):
        """
        Test the overridden save() sets correct slug
        """
        self.post.slug = ''
        self.post.save()
        self.assertEqual(slugify(self.post.title), self.post.slug)


class BlogPageTest(WagtailPageTests):
    """
    Tests blog.models.BlogPage
    """

    fixtures = ['blog/fixtures/test_pages']

    @classmethod
    def setUpTestData(cls):
        cls.index_page = BlogPageIndex.objects.live().first()
        cls.published_blog_page = BlogPage.objects.live().first()

    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_can_create_page(self):
        """
        Test creating a BlogPage under the BlogPageIndex via form with expected data creates the page.
        """
        index_page = BlogPageIndex.objects.live().first()

    def test_get_id_and_slug_url(self):
        """
        Test that BlogPage.
        """
        blog_page = BlogPage.objects.live().first()
        self.assertEqual(f'/blog-index/{blog_page.pk}/{blog_page.slug}/', blog_page.get_id_and_slug_url())

    def test_request_by_id_and_slug_route(self):
        r = self.client.get(self.published_blog_page.get_id_and_slug_url())
        self.assertEqual(200, r.status_code)

    def test_request_by_id_and_slug_route_redirects_on_slug_mismatch(self):
        """
        Test that a GET request to the id_and_slug_url redirects to the correct slug if the requested slug does not
        match the current slug.
        """
        url = self.published_blog_page.get_id_and_slug_url()
        url = f'{url[:-1]}1/'
        r = self.client.get(url)
        self.assertRedirects(
            r, self.published_blog_page.get_id_and_slug_url(),
        )
