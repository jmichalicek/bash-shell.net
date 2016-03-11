from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from models import Project, ProjectNews


def full_project_list(request):
    projects = Project.objects.all().order_by('primary_language__name')

    return render_to_response(
        'bsproject/full_project_list.html',
        {'projects': projects},
        context_instance=RequestContext(request))


def project(request, project_name):
    project = get_object_or_404(Project, name=project_name)

    # Show all of the project news.  In the future this could be too much
    # and a news_archive view would be good, but for my own use it won't be
    # for quite some time.
    project_news = ProjectNews.objects.filter(project=project, published=True,
                                              ).order_by('-date_created')

    return render_to_response(
        'bsproject/project.html',
        {'project': project,
         'project_news': project_news},
        context_instance=RequestContext(request))
