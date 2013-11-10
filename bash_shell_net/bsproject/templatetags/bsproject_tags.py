from django import template

from bsproject.models import Language

register = template.Library()

def get_project_languages():
    return Language.objects.all().order_by('name')

register.assignment_tag(get_project_languages)
