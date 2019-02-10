from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from .feeds import BlogFeedRss
from .sitemaps import BlogSitemap, ProjectSiteMap, ProjectsSiteMap

admin.autodiscover()

sitemaps = {'blog': BlogSitemap, 'project': ProjectSiteMap, 'projects': ProjectsSiteMap}

urlpatterns = [
    re_path(r'^cms/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    # re_path(r'^pages/', include(wagtail_urls)),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {
        'sitemaps': sitemaps
    }),
    url(r'^feeds/rss/', BlogFeedRss()),
    url(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    url(r'^opensource/$', TemplateView.as_view(template_name="open_source.html"), name="opensource"),
    url(r'^oldblog/', include('blog.urls')),
    url(r'^projects/', include('projects.urls')),

    url(r'^', include(wagtail_urls)),
    # url(r'^', include('blog.urls')), # legacy stuff
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
