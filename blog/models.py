from __future__ import absolute_import, unicode_literals, division

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.text import slugify

from django.contrib.auth.models import User

class Tag(models.Model):
    """Category which posts belong to"""
    # name indexed because we order on name
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u'%s' %(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(u'%s' % self.name.lower())
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
    user = models.ForeignKey('accounts.User', null=True, on_delete=models.SET_NULL, default=None,
                             blank=True, db_index=True, related_name='posts')

    slug = models.SlugField(
        help_text='Automatically built from the title.',
        db_index=True,
        blank=True,
        default='',
        max_length=100
    )

    def get_absolute_url(self):
        # make sure the url date is utc.  If not, annoying things happen...
        # either posts created when the day is a day earlier in local time than in UTC
        # become unreachable or everything has to be done in UTC and then the web browser
        # set date and time is incorrect when creating a post.  So allow proper user timezone
        # but create the url always as UTC
        return reverse('blog_post_detail', args=[self.slug])

    def __unicode__(self):
        return u'%s' %(self.title)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(u'%s' % self.title.lower())
        super(Post, self).save(*args, **kwargs)
