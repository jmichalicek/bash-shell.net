from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
import textwrap

register = template.Library()


@register.simple_tag
def clicky_stats_js(*args, **kwargs):
    if settings.ENABLE_CLICKY:
        clicky_string = textwrap.dedent(
            '''
            <script>var clicky_site_ids = clicky_site_ids || []; clicky_site_ids.push(101271437);</script>
            <script async src="//static.getclicky.com/js"></script>
            '''
        )
        return mark_safe(clicky_string)
    return ''
