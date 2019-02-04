from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.models import Page
from wagtail.search import index
from wagtail_blocks.fields import StandardPageBodyStreamField

from .managers import PublishedPostQuerySet


class Tag(models.Model):
    """Category which posts belong to"""
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
    """Model for each separate post"""
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('blog.Tag', blank=True, related_name='posts')
    is_published = models.BooleanField(db_index=True, default=False, blank=True)
    published_date = models.DateTimeField(db_index=True, null=True, default=None, blank=True)
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL, default=None, blank=True,
                             db_index=True, related_name='posts')
    slug = models.SlugField(help_text='Automatically built from the title.', db_index=True, blank=True, default='',
                            max_length=100)
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


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('blog.BlogPost', on_delete=models.CASCADE, related_name='tagged_items')


class BlogPostIndex(Page):
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
        context = super(BlogPostIndex, self).get_context(request)
        context['posts'] = BlogPost.objects.descendant_of(self).live().order_by('-last_published_at')
        return context


class BlogPost(Page):

    template = 'wagtail_templates/blog/post_detail.html'
    parent_page_types = ['BlogPostIndex']
    subpage_types = []

    #body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    # https://github.com/wagtail/bakerydemo/blob/master/bakerydemo/blog/models.py#L75
    # Do I need this and then add it to contentfields?
    # date_published = models.DateField(
    #     "Date article published", blank=True, null=True
    # )

    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    body = StandardPageBodyStreamField(blank=True, null=True, default=None)
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
            'owner', (index.SearchField('email'), index.SearchField('first_name'), index.SearchField('last_name')))
    ]

    def __str__(self):
        return self.title
