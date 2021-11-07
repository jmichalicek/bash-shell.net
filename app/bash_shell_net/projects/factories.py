from django.utils import timezone

from datetime import timedelta
import factory
from factory.django import DjangoModelFactory


class ProjectFactory(DjangoModelFactory):
    is_active = False
    name = factory.Sequence(lambda n: 'Project %03d' % n)
    description = factory.Sequence(lambda n: 'Description of unpublished post %03d' % n)

    class Meta:
        model = 'projects.Project'


class ActiveProjectFactory(ProjectFactory):
    is_active = True

    class Meta:
        model = 'projects.Project'
