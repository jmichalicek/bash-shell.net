from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import index, sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from bash_shell_net.blog.feeds import BlogFeedRss

from .sitemaps import BatchLogPageSitemap, BlogSitemap, OnTapSitemap, ProjectSiteMap, ProjectsSiteMap, RecipePageSitemap

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
    # path('watchman/', include('watchman.urls')),
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path(
        'sitemap.xml',
        index,
        {
            'sitemaps': sitemaps,
        },
    ),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('feeds/blog/rss/', BlogFeedRss()),
    path('about/', TemplateView.as_view(template_name="about.html"), name="about"),
    path('opensource/', TemplateView.as_view(template_name="open_source.html"), name="opensource"),
    path('projects/', include('bash_shell_net.projects.urls')),
    path('', include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
