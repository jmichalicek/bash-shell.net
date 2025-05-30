from django.urls import path

from . import views

urlpatterns = [
    path("<path:slug>/", views.ProjectDetailView.as_view(), name="projects_project_detail"),
    path("", views.ProjectListView.as_view(), name="projects_project_list"),
]
