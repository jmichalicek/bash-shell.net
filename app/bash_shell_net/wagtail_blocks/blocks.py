"""
Extra wagtail blocks for the site.
"""
from django.utils.safestring import mark_safe

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name, guess_lexer


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
    Code block with pygments based code highlighting for wagtail

    This originally comes from https://www.nathanworkman.me/syntax-highlighting-pygments-wagtails/
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

    language = blocks.ChoiceBlock(
        choices=LANGUAGE_CHOICES, required=False, blank=True, default=CodeHighlightLanguage.AUTO
    )
    filename = blocks.CharBlock(required=False, default='')
    display_filename = blocks.BooleanBlock(required=False, default=True)
    code = blocks.TextBlock(required=False, default='')
    line_numbers = blocks.ChoiceBlock(choices=LINE_NUMBER_CHOICES, default=LineNumberStyle.NONE, required=False)

    class Meta:
        """
        Set streamfield icon.
        """

        icon = 'code'
        template = 'wagtail_blocks/codeblock.html'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
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
        context.update(
            {
                'filename': value.get('filename'),
                'display_filename': value.get('display_filename'),
                'language': value.get('lang'),
                'code': mark_safe(highlight(src, lexer, formatter)),
            }
        )
        return context


class DetailImageChooserBlock(blocks.StructBlock):
    """
    ImageBlock with more meta details
    """

    image = ImageChooserBlock()
    caption = blocks.CharBlock(label='Caption', max_length=200, required=False)
    attribution = blocks.CharBlock(required=False)
    license_url = blocks.URLBlock(required=False)
    license_name = blocks.CharBlock(required=False)

    class Meta:
        icon = 'image'
        template = 'wagtail_blocks/detail_image_block.html'

    @property
    def title(self):
        return self.image.title

    def url(self):
        if self.image and self.image.file:
            # tempting to try/except this for the rare occasion where the file does not exist
            # even though the path is set. That raises an exception and in templates this will be
            # the last place it can be caught.
            return self.image.file.url
        print('no image or no url?')
        return ''


class ImageGalleryBlock(blocks.StructBlock):
    image_items = blocks.ListBlock(
        DetailImageChooserBlock(),
        label="Image",
    )

    class Meta:
        template = 'wagtail_blocks/image_gallery.html'
