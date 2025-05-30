from django import template

from ..models import Language

register = template.Library()


def get_project_languages():
    return Language.objects.all().order_by("name")


register.simple_tag(get_project_languages)
