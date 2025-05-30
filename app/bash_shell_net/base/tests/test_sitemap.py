from django.test import TestCase

from freezegun import freeze_time

from bash_shell_net.blog.factories import BlogPageFactory
from bash_shell_net.on_tap.factories import BatchLogPageFactory, OnTapPageFactory, RecipePageFactory
from bash_shell_net.projects.factories import ActiveProjectFactory


class SiteMapTest(TestCase):
    """
    Test sitemaps.xml.

    This does not really belong here, but I guess if I just move sitemaps.py to here, then it would.
    or perhaps it will get its own app because it will pull in stuff from any other app.
    """

    maxDiff = None

    @freeze_time("2022-11-18")
    def test_get(self):
        # working around nonsense with django 4.1 sitemaps which break
        # when there is an empty list of items until the fix is released
        # https://code.djangoproject.com/ticket/34088
        BlogPageFactory()
        OnTapPageFactory()
        RecipePageFactory()
        BatchLogPageFactory()
        ActiveProjectFactory()
        r = self.client.get("/sitemap.xml")
        self.assertEqual(200, r.status_code)
        expected = b'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<sitemap><loc>https://example.com/sitemap-on_tap.xml</loc></sitemap><sitemap><loc>https://example.com/sitemap-on_tap-batches.xml</loc></sitemap><sitemap><loc>https://example.com/sitemap-on_tap-recipes.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-blog.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-project.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-projects.xml</loc><lastmod>2022-11-18T00:00:00+00:00</lastmod></sitemap>\n</sitemapindex>\n'
        self.assertEqual(expected, r.content)
