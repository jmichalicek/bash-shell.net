from typing import TYPE_CHECKING
from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.search import index

from bash_shell_net.blog.models import BlogPageIndexMixin
from bash_shell_net.wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS


if TYPE_CHECKING:
    from wagtail.models import Page as _Page

    class Page(_Page, models.Model):
        pass
else:
    from wagtail.models import Page
    

class Homepage(BlogPageIndexMixin, Page):
    """
    Base homepage for the root of the site
    """

    # Just a dummy page because if I set BlogIndexPage to the site root
    # then it basically breaks everything, because everything needs to be a child
    # of that.
    template = 'base/homepage.html'

    # subpage_types = ['BlogPost']

    def __str__(self) -> str:
        return self.title

    # Defines a method to access the children of the page (e.g. BlogPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # http://docs.wagtail.io/en/latest/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        # TODO: move this to a mixin similar to django's ListView.  WagtailListView or something.
        # try with pagination
        context = super().get_context(request)
        # Why am I not using self.children()?
        return self._get_context(request, context)


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
