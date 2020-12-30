from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPage
from on_tap.models import OnTapPage, RecipePage, BatchLogPage
from projects.models import Project
from wagtail.contrib.sitemaps import Sitemap as WagtailSitemap
from wagtail.core.models import Orderable, Page


class BlogSitemap(WagtailSitemap):
    """
    Sitemap for posts
    """

    priority = 0.5
    limit = 50

    def items(self):
        return BlogPage.objects.live().public().order_by('-first_published_at')

    def lastmod(self, obj):
        return obj.last_published_at

    def location(self, obj):
        return obj.get_id_and_slug_url()


class OnTapSitemap(WagtailSitemap):
    """
    Sitemap for posts
    """

    # changefreq = "never"
    limit = 50
    priority = 0.5
    protocol = 'https'

    def items(self):
        return OnTapPage.objects.live().public().order_by('-first_published_at')

    def lastmod(self, obj):
        return obj.last_published_at


class RecipePageSitemap(WagtailSitemap):
    """
    Sitemap for on_tap.RecipePage
    """

    # changefreq = "never"
    limit = 50
    priority = 0.5
    protocol = 'https'

    def items(self):
        return RecipePage.objects.live().public().order_by('-first_published_at')

    def lastmod(self, obj):
        return obj.last_published_at


class BatchLogPageSitemap(WagtailSitemap):
    """
    Sitemap for on_tap.BatchLogPage
    """

    # changefreq = "never"
    limit = 50
    priority = 0.5
    protocol = 'https'

    def items(self):
        return BatchLogPage.objects.live().public().order_by('-first_published_at')

    def lastmod(self, obj):
        return obj.last_published_at


class ProjectSiteMap(Sitemap):
    """List the /blog/projects/ page"""

    priority = 0.5
    limit = 50

    def items(self):
        return [reverse('projects_project_list')]

    def location(self, obj):
        # we overwrite this to stop it calling get_absolute_url
        return obj


class ProjectsSiteMap(Sitemap):
    """
    Lists posts in the projects cateogry.  This is
    to separate them out from the blog posts since the url
    may change for them.
    """

    priorit = 0.5
    limit = 50

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        # Who needs consistently named fields?  not me...
        # I should fix that.
        return obj.modified_date
