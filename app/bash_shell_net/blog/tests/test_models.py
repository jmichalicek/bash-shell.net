import unittest

from wagtail.test.utils import WagtailPageTestCase

from bash_shell_net.base.test_utils import add_wagtail_factory_page
from bash_shell_net.blog.factories import BlogPageFactory, BlogPageIndexFactory
from bash_shell_net.blog.models import BlogPage, BlogPageIndex


class BlogPageTest(WagtailPageTestCase):
    """
    Tests blog.models.BlogPage
    """

    index_page: BlogPageIndex
    published_blog_page: BlogPage
    blog_index_page: BlogPageIndex
    blog_page: BlogPage

    @classmethod
    def setUpTestData(cls):
        cls.blog_index_page = add_wagtail_factory_page(BlogPageIndexFactory)

    def setUp(self):
        super().setUp()
        self.blog_page = add_wagtail_factory_page(BlogPageFactory, parent_page=self.blog_index_page)
        self.login()

    @unittest.skip("Skipped because I have not written this but at least I will see skipped tests now.")
    def test_can_create_page(self):
        """
        Test creating a BlogPage under the BlogPageIndex via form with expected data creates the page.
        """
        pass
