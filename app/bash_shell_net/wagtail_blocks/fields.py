from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .blocks import CodeBlock, DetailImageChooserBlock, ImageGalleryBlock

STANDARD_STREAMFIELD_FIELDS = [
    ("heading", blocks.CharBlock(classname="full title")),
    (
        "paragraph",
        blocks.RichTextBlock(
            features=[
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
                "ol",
                "ul",
                "bold",
                "italic",
                "code",
                "superscript",
                "subscript",
                "strikethrough",
                "blockquote",
                "link",
                "document-link",
                "image",
                "embed",
            ]
        ),
    ),
    ("code", CodeBlock()),
    ("quote", blocks.BlockQuoteBlock()),
    ("other_page", blocks.PageChooserBlock()),
    ("document", DocumentChooserBlock()),
    ("image", ImageChooserBlock(template="wagtail_blocks/image.html")),
    ("image_detail", DetailImageChooserBlock()),
    ("image_gallery", ImageGalleryBlock()),
    # ('snippet', SnippetChooserBlock()), these are specific to a snippet model and I have none
    ("embed", EmbedBlock()),
    ("text", blocks.TextBlock()),
    ("raw_html", blocks.RawHTMLBlock()),
]
