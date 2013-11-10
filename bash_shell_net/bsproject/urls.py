from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       url(r'^(?P<project_name>.+)/$', 'bsproject.views.project', name='bsproject_project'),
                       url(r'^$', 'bsproject.views.full_project_list', name='bsproject_full_list'),
                       )
