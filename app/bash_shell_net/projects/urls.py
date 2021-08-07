from django.conf.urls import *

from . import views

urlpatterns = [
    url(r'^(?P<slug>.+)/$', views.ProjectDetailView.as_view(), name='projects_project_detail'),
    url(r'^$', views.ProjectListView.as_view(), name='projects_project_list'),
]
