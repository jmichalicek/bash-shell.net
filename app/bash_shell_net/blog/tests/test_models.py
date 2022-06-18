import unittest

from wagtail.test.utils import WagtailPageTests

from bash_shell_net.base.test_utils import add_wagtail_factory_page
from bash_shell_net.blog.factories import BlogPageFactory, BlogPageIndexFactory
from bash_shell_net.blog.models import BlogPage, BlogPageIndex


class BlogPageTest(WagtailPageTests):
    """
    Tests blog.models.BlogPage
    """

    # fixtures = ["bash_shell_net/blog/fixtures/test_pages"]

    index_page: BlogPageIndex
    published_blog_page: BlogPage

    @classmethod
    def setUpTestData(cls):
        cls.blog_index_page: BlogPageIndex = add_wagtail_factory_page(BlogPageIndexFactory)
        cls.blog_page: BlogPage = add_wagtail_factory_page(BlogPageFactory, parent_page=cls.blog_index_page)

    @unittest.skip("Skipped because I have not written this but at least I will see skipped tests now.")
    def test_can_create_page(self):
        """
        Test creating a BlogPage under the BlogPageIndex via form with expected data creates the page.
        """
        pass

    def test_get_id_and_slug_url(self):
        """
        Test that BlogPage.
        """
        self.assertEqual(
            f'/{self.blog_index_page.slug}/{self.blog_page.pk}/{self.blog_page.slug}/',
            self.blog_page.get_id_and_slug_url(),
        )

    def test_request_by_id_and_slug_route(self):
        r = self.client.get(self.blog_page.get_id_and_slug_url())
        self.assertEqual(200, r.status_code)

    def test_request_by_id_and_slug_route_redirects_on_slug_mismatch(self):
        """
        Test that a GET request to the id_and_slug_url redirects to the correct slug if the requested slug does not
        match the current slug.
        """
        url = self.blog_page.get_id_and_slug_url()
        url = f"{url[:-1]}1/"
        r = self.client.get(url)
        self.assertRedirects(
            r,
            self.blog_page.get_id_and_slug_url(),
        )
