from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from sitemaps import *
from feeds import BlogFeedRss



sitemaps = {'blog': BlogSitemap,
            'project': ProjectSiteMap,
            'projects': ProjectsSiteMap,}

urlpatterns = patterns('',
                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^sitemap\.xml$','django.contrib.sitemaps.views.sitemap',{'sitemaps': sitemaps}),
                       url(r'^feeds/rss/',BlogFeedRss()),
                       url(r'^blog/', include('blog.urls')),
                       url(r'^projects/', include('projects.urls')),
                       url(r'^old_blog/',include('bsblog.urls')),
                       url(r'^old_projects/', include('bsproject.urls')),
                       url(r'^$',include('blog.urls')),
                       )
