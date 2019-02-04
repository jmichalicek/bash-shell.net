"""
Code block with pygments based code highlighting for wagtail

This originally comes from https://www.nathanworkman.me/syntax-highlighting-pygments-wagtails/

"""
from django.utils.safestring import mark_safe

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name, guess_lexer

from wagtail.core import blocks


class LineNumberStyle:
    NONE = ''
    TABLE = 'table'
    INLINE = 'inline'


# This is a bit tedious right now, but almost always ends up a good idea in the end...
class CodeHighlightLanguage:
    AUTO = ''
    BASH = 'bash'
    C = 'c'
    C_SHARP = 'csharp'
    CPP = 'cpp'
    CSS = 'css'
    DJANGO_TEMPLATE = 'htmldjango'
    DOCKERFILE = 'docker'
    ELIXIR = 'elixir'
    GNU_MAKE = 'make'
    GO = 'go'
    HTML = 'html'
    JAVA = 'java'
    JAVASCRIPT = 'javascript'
    JSON = 'json'
    LISP = 'lisp'
    NGINX = 'nginx'
    PERL = 'perl'
    PHP = 'php'
    PYTHON = 'python'
    REACT_JSX = 'jsx'
    RUBY = 'ruby'
    RUBY_TEMPLATE = 'erb'
    SASS = 'sass'
    SCSS = 'scss'
    SQL = 'sql'
    SWIFT = 'swift'
    TERRAFORM = 'terraform'
    WINDOWS_BATCH = 'batch'
    YAML = 'yaml'


class CodeBlock(blocks.StructBlock):
    """
    Code Highlighting Block.
    """

    LANGUAGE_CHOICES = (
        (CodeHighlightLanguage.AUTO, 'Auto'),
        (CodeHighlightLanguage.BASH, 'Bash/Shell'),
        (CodeHighlightLanguage.WINDOWS_BATCH, 'Batch'),
        (CodeHighlightLanguage.C, 'C'),
        (CodeHighlightLanguage.CPP, 'C++'),
        (CodeHighlightLanguage.C_SHARP, 'C#'),
        (CodeHighlightLanguage.CSS, 'CSS'),
        (CodeHighlightLanguage.DOCKERFILE, 'Dockerfile'),
        (CodeHighlightLanguage.ELIXIR, 'Elixir'),
        (CodeHighlightLanguage.GO, 'Go'),
        (CodeHighlightLanguage.DJANGO_TEMPLATE, 'Django Template'),
        (CodeHighlightLanguage.HTML, 'HTML'),
        (CodeHighlightLanguage.JAVASCRIPT, 'JavaScript'),
        (CodeHighlightLanguage.JSON, 'JSON'),
        (CodeHighlightLanguage.LISP, 'Lisp'),
        (CodeHighlightLanguage.GNU_MAKE, 'Makefile'),
        (CodeHighlightLanguage.NGINX, 'NGiNX Config'),
        (CodeHighlightLanguage.PERL, 'Perl'),
        (CodeHighlightLanguage.PHP, 'PHP'),
        (CodeHighlightLanguage.PYTHON, 'Python'),
        (CodeHighlightLanguage.REACT_JSX, 'React JSX'),
        (CodeHighlightLanguage.RUBY, 'Ruby'),
        (CodeHighlightLanguage.RUBY_TEMPLATE, 'Ruby Template/ERB'),
        (CodeHighlightLanguage.SASS, 'SASS'),
        (CodeHighlightLanguage.SCSS, 'SCSS'),
        (CodeHighlightLanguage.SQL, 'SQL'),
        (CodeHighlightLanguage.TERRAFORM, 'Terraform'),
        (CodeHighlightLanguage.YAML, 'YAML'),
    )

    LINE_NUMBER_CHOICES = (
        (LineNumberStyle.NONE, 'None'),
        (LineNumberStyle.TABLE, 'Table'),
        (LineNumberStyle.INLINE, 'Inline'),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES, required=False, blank=True,
                                  default=CodeHighlightLanguage.AUTO)
    code = blocks.TextBlock(required=False, default='')
    line_numbers = blocks.ChoiceBlock(choices=LINE_NUMBER_CHOICES, default=LineNumberStyle.NONE, required=False)

    class Meta:
        """
        Set streamfield icon.
        """
        icon = 'code'

    def render(self, value, context=None):
        """Render codeblock."""
        src = value.get('code') or ''
        src = src.strip('\n')
        lang = value.get('language') or ''
        line_numbers = value['line_numbers']

        if lang:
            lexer = get_lexer_by_name(lang)
        else:
            lexer = guess_lexer(src)
        formatter = get_formatter_by_name(
            'html',
            linenos=line_numbers,
            cssclass='codehilite',
            style='default',
            noclasses=False,
        )
        return mark_safe(highlight(src, lexer, formatter))
