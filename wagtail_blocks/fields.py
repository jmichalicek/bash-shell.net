from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail_blocks.code_block import CodeBlock

STANDARD_STREAMFIELD_FIELDS = [
    ('heading', blocks.CharBlock(classname="full title")),
    ('paragraph', blocks.RichTextBlock()),
    ('code', CodeBlock()),
    ('quote', blocks.BlockQuoteBlock()),
    ('other_page', blocks.PageChooserBlock()),
    ('document', DocumentChooserBlock()),
    ('image', ImageChooserBlock()),
    # ('snippet', SnippetChooserBlock()), these are specific to a snippet model and I have none
    ('embed', EmbedBlock()),
    ('text', blocks.TextBlock()),
    ('raw_html', blocks.RawHTMLBlock()),
]
