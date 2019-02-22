from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models

from blog.models import BlogPage
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.search import index
from wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS


class Homepage(Page):
    """
    Base homepage for the root of the site
    """

    template = 'wagtail_templates/base/homepage.html'

    # subpage_types = ['BlogPost']

    # Defines a method to access the children of the page (e.g. BlogPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # http://docs.wagtail.io/en/latest/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        # not paginated
        # context = super().get_context(request)
        # context['posts'] = BlogPost.objects.descendant_of(self).live().order_by('-last_published_at')

        # TODO: move this to a mixin similar to django's ListView.  WagtailListView or something.
        # try with pagination
        context = super().get_context(request)
        posts = BlogPage.objects.live().order_by('-last_published_at')
        paginator = Paginator(posts, 15)  # Show 5 resources per page
        page_number = request.GET.get('page')
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)

        # make the variable 'resources' available on the template
        context['paginator'] = paginator
        context['posts'] = page.object_list
        context['page_obj'] = page
        return context


class StandardPage(Page):
    """
    A generic content page. Useful for about page, etc. where it's not part of another
    app or browsing tree.
    """
    template = 'wagtail_templates/base/standard_page.html'

    introduction = models.TextField(help_text='Text to describe the page', blank=True)

    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                              help_text='Landscape mode only; horizontal width between 1000px and 3000px.')
    body = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]
