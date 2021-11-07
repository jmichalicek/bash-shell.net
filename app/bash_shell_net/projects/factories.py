import factory
from factory.django import DjangoModelFactory


class ProjectFactory(DjangoModelFactory):
    is_active = False
    name = factory.Sequence(lambda n: 'Project {n:%03}')
    description = factory.Sequence(lambda n: 'Description of unpublished post {n:03}')

    class Meta:
        model = 'projects.Project'


class ActiveProjectFactory(ProjectFactory):
    is_active = True

    class Meta:
        model = 'projects.Project'
