from __future__ import absolute_import, unicode_literals, division

from django import template

from ..models import Language

register = template.Library()

def get_project_languages():
    return Language.objects.all().order_by('name')

register.assignment_tag(get_project_languages)
