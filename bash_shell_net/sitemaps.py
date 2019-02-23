from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import BlogPage
from projects.models import Project


class BlogSitemap(Sitemap):
    """Sitemap for posts"""
    changefreq = "never"
    priority = 0.5

    def items(self):
        return BlogPage.objects.live().order_by('first_published_at')

    def lastmod(self, obj):
        return obj.last_published_at


class ProjectSiteMap(Sitemap):
    """List the /blog/projects/ page"""
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return [reverse('projects_project_list')]

    def location(self, obj):
        # we overwrite this to stop it calling get_absolute_url
        return obj


class ProjectsSiteMap(Sitemap):
    """Lists posts in the projects cateogry.  This is
    to separate them out from the blog posts since the url
    may change for them."""
    changefreq = "monthly"
    priorit = 0.5

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        # Who needs consistently named fields?  not me...
        # I should fix that.
        return obj.modified_date
