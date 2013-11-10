from django.conf.urls.defaults import *
from django.conf import settings
from models import Post

post_limit = getattr(settings, 'BSBLOG_POSTS_LIMIT', 10)

urlpatterns = patterns('',
                       url(r'^(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$',
                           'bsblog.views.item', name='bsblog_full_post_url'),
                       url(r'^archive/$', 'bsblog.views.archive', name='bsblog_archive'),
                       url(r'^(?P<page>\d+)/$', 'bsblog.views.index', {'post_limit':post_limit}, name='bsblog_main'),
                       url(r'^$','bsblog.views.index', {'post_limit':post_limit}, name='bsblog_main'),
                       url(r'^(?P<category>\w+)/$', 'bsblog.views.index', name='bsblog_category'),
                       url(r'^(?P<category>\w+)/(?P<page>\d+)/$', 'bsblog.views.index', name='bsblog_category'),
                       )
