from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.search import index
from wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS

from .managers import PublishedPostQuerySet


class Tag(models.Model):
    """
    Category which posts belong to

    Legacy model from old, pre-wagtail blog
    """

    # name indexed because we order on name
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name.lower())
        super(Tag, self).save(*args, **kwargs)


class Post(models.Model):
    """
    Model for each separate post

    Legacy model from old, pre-wagtail blog
    """

    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('blog.Tag', blank=True, related_name='posts')
    is_published = models.BooleanField(db_index=True, default=False, blank=True)
    published_date = models.DateTimeField(db_index=True, null=True, default=None, blank=True)
    user = models.ForeignKey(
        'accounts.User',
        null=True,
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        db_index=True,
        related_name='posts',
    )
    slug = models.SlugField(
        help_text='Automatically built from the title.', db_index=True, blank=True, default='', max_length=100
    )
    objects = PublishedPostQuerySet.as_manager()

    def get_absolute_url(self):
        # make sure the url date is utc.  If not, annoying things happen...
        # either posts created when the day is a day earlier in local time than in UTC
        # become unreachable or everything has to be done in UTC and then the web browser
        # set date and time is incorrect when creating a post.  So allow proper user timezone
        # but create the url always as UTC
        if self.is_published and self.published_date and self.published_date <= timezone.now():
            return reverse('blog_post_detail', args=[self.slug])
        else:
            return reverse('blog_post_preview', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title.lower())
        super(Post, self).save(*args, **kwargs)


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPage', on_delete=models.CASCADE, related_name='tagged_items')


class BlogPageIndex(RoutablePageMixin, Page):
    """
    Index page to list blog posts
    """

    # For pagination, look here: https://stackoverflow.com/questions/40365500/pagination-in-wagtail
    # and for general: https://github.com/wagtail/bakerydemo/blob/master/bakerydemo/blog/models.py#L133
    template = 'wagtail_templates/blog/post_index.html'

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
        posts = BlogPage.objects.descendant_of(self).live().order_by('-last_published_at')
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

    @route(r'^(?P<id>\d+)/(?P<slug>[-_\w]+)/$', name="blog_post_by_id_and_slug")
    def blog_post_by_id_and_slug(self, request, id, slug, *args, **kwargs) -> HttpResponse:
        """
        Look up post using the a "slug" which is really the post id followed by the actual slug
        """
        page = BlogPage.objects.filter(pk=id)
        if not getattr(request, 'is_preview', False):
            page = page.live()
        page = page.first()
        if not page:
            raise Http404

        if not page.slug == slug:
            # using this for efficiency vs page.get_id_and_slug_url()
            # TODO: review wagtail docs to see if there is a simple and efficient way to have it just default
            # to the id and slug url for page.url
            return HttpResponseRedirect(
                self.url + self.reverse_subpage('blog_post_by_id_and_slug', kwargs={'id': id, 'slug': page.slug})
            )
        # or return blog_page.serve(request, *args, **kwargs) ??
        return page.serve(request, *args, **kwargs)


class BlogPage(Page):

    template = 'wagtail_templates/blog/post_detail.html'
    parent_page_types = ['BlogPageIndex']
    subpage_types = []

    # body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    # https://github.com/wagtail/bakerydemo/blob/master/bakerydemo/blog/models.py#L75
    # Do I need this and then add it to contentfields?
    # date_published = models.DateField(
    #     "Date article published", blank=True, null=True
    # )

    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    body = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None)
    # body = StreamField(
    #     [
    #         ('heading', blocks.CharBlock(classname="full title")),
    #         ('paragraph', blocks.RichTextBlock()),
    #         ('code', CodeBlock()),
    #         ('quote', blocks.BlockQuoteBlock()),
    #         ('other_page', blocks.PageChooserBlock()),
    #         ('document', DocumentChooserBlock()),
    #         ('image', ImageChooserBlock()),
    #         # ('snippet', SnippetChooserBlock()),
    #         ('embed', EmbedBlock()),
    #         ('text', blocks.TextBlock()),
    #         ('raw_html', blocks.RawHTMLBlock()),
    #
    #         # just testing these... no idea how useful
    #         # ('single_line', blocks.CharBlock()),
    #         # ('email', blocks.EmailBlock()),
    #         # ('integer', blocks.IntegerBlock()),
    #         # ('float', blocks.FloatBlock()),
    #         # ('decimal', blocks.DecimalBlock()),
    #         # ('url', blocks.URLBlock()),
    #         # ('boolean', blocks.BooleanBlock()),
    #         # ('date', blocks.DateBlock()),
    #         # ('time', blocks.TimeBlock()),
    #         # ('datetime', blocks.DateTimeBlock()),
    #     ],
    #     null=True,
    #     blank=True,
    #     default=None,
    # )

    content_panels = Page.content_panels + [StreamFieldPanel('body')]
    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('body'),
        index.SearchField('tags'),
        index.RelatedFields(
            'owner', (index.SearchField('email'), index.SearchField('first_name'), index.SearchField('last_name'))
        ),
    ]

    def __str__(self):
        return self.title

    @cached_property
    def id_and_slug_url(self) -> str:
        # tempted to just put this in actual cache instead, but that feels dirty on a model even though this model
        # is really more akin to a django view
        return self.get_id_and_slug_url()

    def get_context(self, request):
        context = super().get_context(request)

        if self.first_published_at and self.pk:
            # TODO: Is this really going to happen? Same first published but id lower? or higher?
            # I think it would work just as well to just make this:
            # BP.live().filter(first_published_at__lte=self.first_published_at).exclude(pk=self.pk).order_by('-first_published_at', 'id')
            previous_post_q = Q(first_published_at=self.first_published_at, id__lt=self.id)
            previous_post_q = previous_post_q | Q(first_published_at__lt=self.first_published_at)
            previous_post = (
                BlogPage.objects.live()
                .filter(previous_post_q)
                .exclude(pk=self.pk)
                .order_by('-first_published_at', 'id')
                .first()
            )
        else:
            previous_post = BlogPage.objects.live().order_by('-first_published_at', 'id').first()

        if self.first_published_at and self.pk:
            next_post_q = Q(first_published_at=self.first_published_at, id__gt=self.id)
            # is there a better way to handle this being used in unpublished previews?
            next_post_q = next_post_q | Q(first_published_at__gt=self.first_published_at)
            next_post = BlogPage.objects.live().filter(next_post_q)
            next_post = next_post.exclude(pk=self.pk).order_by('first_published_at', '-id').first()
        else:
            next_post = None
        context['previous_post'] = previous_post
        context['next_post'] = next_post
        return context

    def get_id_and_slug_url(self) -> str:
        """
        Returns the url path for post_by_id_and_slug route
        """
        # lightly modified from https://github.com/wagtail/wagtail/blob/ba6f94def17b8bbc66002cbc7af60ed422658ff1/wagtail/contrib/routable_page/templatetags/wagtailroutablepage_tags.py#L10
        parent = self.get_parent().specific
        base_url = parent.relative_url(self.get_site())
        routed_url = parent.reverse_subpage('blog_post_by_id_and_slug', kwargs={'id': self.pk, 'slug': self.slug})
        if not base_url.endswith('/'):
            base_url += '/'
        return base_url + routed_url
