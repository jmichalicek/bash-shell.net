import factory
from factory.django import DjangoModelFactory

from bash_shell_net.projects.models import Project


class ProjectFactory(DjangoModelFactory):
    is_active = False
    name = factory.Sequence(lambda n: "Project {n:%03}")
    description = factory.Sequence(lambda n: "Description of unpublished post {n:03}")

    class Meta:
        model = Project


class ActiveProjectFactory(ProjectFactory):
    is_active = True

    class Meta:
        model = Project
