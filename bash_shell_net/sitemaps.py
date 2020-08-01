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


class OnTapSitemap(WagtailSitemap):
    """
    Sitemap for posts
    main_298a6006830dacabb4569bb44b23e66b2a7b1150
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
    Sitemap for posts
    main_298a6006830dacabb4569bb44b23e66b2a7b1150
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
    Sitemap for posts
    main_298a6006830dacabb4569bb44b23e66b2a7b1150
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
