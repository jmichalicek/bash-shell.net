from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from bash_shell_net.blog.models import BlogPageIndex
from bash_shell_net.wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS


class Homepage(BlogPageIndex):
    """
    Base homepage for the root of the site
    """

    # Just a dummy page because if I set BlogIndexPage to the site root
    # then it basically breaks everything, because everything needs to be a child
    # of that.


class StandardPage(Page):
    """
    A generic content page. Useful for about page, etc. where it's not part of another
    app or browsing tree.
    """

    template = "base/standard_page.html"

    introduction = models.TextField(help_text="Text to describe the page", blank=True)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
    )
    body = StreamField(
        STANDARD_STREAMFIELD_FIELDS,
        blank=True,
        null=True,
        default=None,
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def __str__(self) -> str:
        return self.title
