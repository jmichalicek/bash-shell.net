from django.views.generic import DetailView, ListView

from .models import Project


class ProjectListView(ListView):
    """
    Public list of projects
    """

    model = Project
    queryset = Project.objects.filter(is_active=True).order_by('primary_language__name', 'name')
    template_name = 'projects/projects_list.html'


class ProjectDetailView(DetailView):
    model = Project
    queryset = Project.objects.filter(is_active=True)
    template_name = 'projects/project_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(**kwargs)
        context.update({'project_news': self.object.project_news.filter(is_published=True).order_by('-created_date')})

        return context
