from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

import markdown

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    return markdown.markdown(value, output_format='html', extensions=settings.MARKDOWN_EXTENSIONS)


@register.tag(name="markdown")
def markdown_tag(parser, token):
    """
    Borrowed from
    https://github.com/trentm/django-markdown-deux/blob/master/lib/markdown_deux/templatetags/markdown_deux_tags.py
    The style arg could be updated to allow using specific markdown extensions - I assume that is what it does
    in markdown_deux anyway.
    """
    nodelist = parser.parse(('endmarkdown',))
    bits = token.split_contents()
    if len(bits) == 1:
        style = "default"
    elif len(bits) == 2:
        style = bits[1]
    else:
        raise template.TemplateSyntaxError("`markdown` tag requires exactly zero or one arguments")
    parser.delete_first_token()  # consume '{% endmarkdown %}'
    return MarkdownNode(style, nodelist)


class MarkdownNode(template.Node):
    """
    For rendering markdown blocks
    """

    def __init__(self, style, nodelist):
        self.style = style
        self.nodelist = nodelist

    def render(self, context):
        value = self.nodelist.render(context)
        return mark_safe(markdown.markdown(value, extensions=settings.MARKDOWN_EXTENSIONS))
