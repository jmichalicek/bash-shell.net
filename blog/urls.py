from __future__ import unicode_literals, absolute_import

from django.conf.urls import url

from . import views


urlpatterns = [
    # legacy url.
    url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$',
        views.PostDetailView.as_view(), name='legacy_post_detail'),
    url(r'^(?P<slug>[-\w]+)/$', views.PostDetailView.as_view(), name='blog_post_detail'),
    url(r'^$', views.PostListView.as_view(), name='blog_post_list'),
    ]
