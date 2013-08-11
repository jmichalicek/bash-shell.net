from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse
from bsblog.models import Post

class BlogSitemap(Sitemap):
    """Sitemap for posts"""
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.filter(published=True).filter(category__name="Blog")

    def lastmod(self, obj):
        return obj.created_date

class ProjectSiteMap(Sitemap):
    """List the /blog/projects/ page"""
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        #return [self]
        return [reverse('bsproject_full_list')]

    def location(self,obj):
        # we overwrite this to stop it calling get_absolute_url
        return obj

class ProjectsSiteMap(Sitemap):
    """Lists posts in the projects cateogry.  This is
    to separate them out from the blog posts since the url
    may change for them."""
    changefreq = "monthly"
    priorit = 0.5

    def items(self):
        return Post.objects.filter(published=True).filter(category__name="Projects")

    def lastmod(self, obj):
        return obj.created_date
