from django.test import TestCase


class SiteMapTest(TestCase):
    """
    Test sitemaps.xml.

    This does not really belong here, but I guess if I just move sitemaps.py to here, then it would.
    or perhaps it will get its own app because it will pull in stuff from any other app.
    """
    maxDiff = None

    def test_get(self):
        r = self.client.get('/sitemap.xml')
        self.assertEqual(200, r.status_code)
        expected = '<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<sitemap><loc>https://example.com/sitemap-on_tap.xml</loc></sitemap><sitemap><loc>https://example.com/sitemap-on_tap-batches.xml</loc></sitemap><sitemap><loc>https://example.com/sitemap-on_tap-recipes.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-blog.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-project.xml</loc></sitemap><sitemap><loc>http://example.com/sitemap-projects.xml</loc></sitemap>\n</sitemapindex>\n'
        self.assertEqual(expected, r.content.decode('utf-8'))
