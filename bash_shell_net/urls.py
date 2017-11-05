from django.conf.urls import include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.flatpages.sitemaps import FlatPageSitemap
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from .sitemaps import *
from .feeds import BlogFeedRss



sitemaps = {'blog': BlogSitemap,
            'project': ProjectSiteMap,
            'projects': ProjectsSiteMap,}

urlpatterns = [
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}),
    url(r'^feeds/rss/', BlogFeedRss()),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    url(r'^opensource/$', TemplateView.as_view(template_name="open_source.html"), name="opensource"),
    url(r'^blog/', include('blog.urls')),
    url(r'^projects/', include('projects.urls')),
    url(r'^', include('blog.urls')),
]
