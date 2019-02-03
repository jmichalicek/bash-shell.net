from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, PageManager, PageQuerySet
# from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

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



# class BlogPostIndex(Page):
#     """
#     Index page to list blog posts
#     """


class BlogPost(Page):

    template = 'wagtail_templates/blog/post_detail.html'

    #body = StreamField(BaseStreamBlock(), verbose_name="Page body", blank=True)

    # https://github.com/wagtail/bakerydemo/blob/master/bakerydemo/blog/models.py#L75
    # Do I need this and then add it to contentfields?
    # date_published = models.DateField(
    #     "Date article published", blank=True, null=True
    # )

    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    body = StreamField(
        [
            ('heading', blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ('raw_html', blocks.RawHTMLBlock()),
            ('quote', blocks.BlockQuoteBlock()),
            ('email', blocks.EmailBlock()),
            ('other_page', blocks.PageChooserBlock()),
            ('document', DocumentChooserBlock()),
            ('image', ImageChooserBlock()),
            # ('snippet', SnippetChooserBlock()),
            ('embed', EmbedBlock()),

            # just testing these... no idea how useful
            ('single_line', blocks.CharBlock()),
            ('text', blocks.TextBlock()),
            ('integer', blocks.IntegerBlock()),
            ('float', blocks.FloatBlock()),
            ('decimal', blocks.DecimalBlock()),
            ('url', blocks.URLBlock()),
            ('boolean', blocks.BooleanBlock()),
            ('date', blocks.DateBlock()),
            ('time', blocks.TimeBlock()),
            ('datetime', blocks.DateTimeBlock()),
        ],
        null=True,
        blank=True,
        default=None,
    )

    content_panels = Page.content_panels + [StreamFieldPanel('body')]
    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
    ]

    def __str__(self):
        return self.title
