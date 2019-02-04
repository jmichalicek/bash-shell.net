from wagtail.core import blocks
from wagtail.core.fields import StreamField
# from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_blocks.code_block import CodeBlock


class StandardPageBodyStreamField(StreamField):
    def __init__(self, *args, **kwargs):
        super().__init__([
            ('heading', blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ('code', CodeBlock()),
            ('quote', blocks.BlockQuoteBlock()),
            ('other_page', blocks.PageChooserBlock()),
            ('document', DocumentChooserBlock()),
            ('image', ImageChooserBlock()),
            # ('snippet', SnippetChooserBlock()),
            ('embed', EmbedBlock()),
            ('text', blocks.TextBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
        ])
