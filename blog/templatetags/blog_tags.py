from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

import markdown

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    return markdown.markdown(value, output_format='html5', extensions=settings.MARKDOWN_EXTENSIONS)
