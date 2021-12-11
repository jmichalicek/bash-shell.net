from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^(?P<slug>.+)/$', views.ProjectDetailView.as_view(), name='projects_project_detail'),
    re_path(r'^$', views.ProjectListView.as_view(), name='projects_project_list'),
]
