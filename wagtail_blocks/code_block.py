"""
Code block with pygments based code highlighting for wagtail

This originally comes from https://www.nathanworkman.me/syntax-highlighting-pygments-wagtails/

"""
from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

from wagtail.wagtailcore import blocks


class CodeBlock(blocks.StructBlock):
    """
    Code Highlighting Block.
    """

    LANGUAGE_CHOICES = (
        ('bash', 'Bash/Shell'),
        ('batch', 'Batch'),
        ('c', 'C'),
        ('cpp', 'C++'),
        ('csharp', 'C#'),
        ('css', 'CSS'),
        ('docker', 'Dockerfile'),
        ('elixir', 'Elixir'),
        ('go', 'Go'),
        ('graphql', 'GraphQL'),
        ('htmldjango', 'Django Template'),
        ('html', 'HTML'),
        ('javascript', 'JavaScript'),
        ('json', 'JSON'),
        ('lisp', 'Lisp'),
        ('make', 'Makefile'),
        ('perl', 'Perl'),
        ('php', 'PHP'),
        ('python', 'Python'),
        ('jsx', 'React JSX'),
        ('ruby', 'Ruby'),
        ('sql', 'SQL'),
        ('yaml', 'YAML'),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = blocks.TextBlock()

    class Meta:
        """
        Set streamfield icon.
        """
        icon = 'code'

    def render(self, value, context=None):
        """Render codeblock."""
        src = value['code'].strip('\n')
        lang = value['language']

        lexer = get_lexer_by_name(lang)
        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass='syntax',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))
