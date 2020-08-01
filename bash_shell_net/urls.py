from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap, index
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from .feeds import BlogFeedRss
from .sitemaps import BlogSitemap, ProjectSiteMap, ProjectsSiteMap, OnTapSitemap, RecipePageSitemap, BatchLogPageSitemap

admin.autodiscover()

sitemaps = {
    'on_tap': OnTapSitemap,
    'on_tap-batches': BatchLogPageSitemap,
    'on_tap-recipes': RecipePageSitemap,
    'blog': BlogSitemap,
    'project': ProjectSiteMap,
    'projects': ProjectsSiteMap,
}

urlpatterns = [
    re_path(r'^cms/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),
    re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('sitemap.xml', index, {'sitemaps': sitemaps,}),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    re_path(r'^feeds/rss/', BlogFeedRss()),
    re_path(r'^about/$', TemplateView.as_view(template_name="about.html"), name="about"),
    re_path(r'^opensource/$', TemplateView.as_view(template_name="open_source.html"), name="opensource"),
    re_path(r'^archives/', include('blog.urls')),
    re_path(r'^projects/', include('projects.urls')),
    re_path(r'^', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
