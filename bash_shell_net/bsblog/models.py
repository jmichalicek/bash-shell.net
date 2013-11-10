from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

import markdown

from taxonomy import models as taxonomy

# Create your models here.
# So that user can be extended more easily
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)

    def __unicode__(self):
        return u'%s' %(self.user.username)

class Category(models.Model):
    """Category which posts belong to"""
    # name indexed because we order on name
    name = models.CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return u'%s' %(self.name)

## Add new Project model and make projects not a blog post?
## maybe whole new projects app
class Post(taxonomy.TaxonomyMember):
    """Model for each separate post"""
    title = models.CharField(max_length=100)
    text_html = models.TextField(blank=True)
    text_markdown = models.TextField()
    # Why no auto_now_add here?
    created_date = models.DateTimeField('Date Created', db_index=True)
    category = models.ForeignKey(Category, db_index=True)
    user_profile = models.ForeignKey(UserProfile)
    published = models.BooleanField(db_index=True)

    slug = models.SlugField(
        unique_for_date='created_date',
        help_text='Automatically built from the title.',
        db_index=True
    )

    @models.permalink
    def get_absolute_url(self):
        #return "/%s/%s/" %(self.created_date.strftime("%Y/%b/%d").lower(), self.slug)
        year = self.created_date.strftime('%Y')
        month = self.created_date.strftime('%b').lower()
        day = self.created_date.strftime('%d')
        return ('bsblog_full_post_url', [year, month, day, self.slug])

    def __unicode__(self):
        return u'%s' %(self.title)

    def save(self):
        self.text_html = markdown.markdown(self.text_markdown, safe_mode=False)
        super(Post,self).save()

# signal handlers
def create_profile(sender, **kwargs):
    # The check for raw makes this not run when the user was loaded
    # from a fixture
    if kwargs.get('created') and not kwargs.get('raw', False):
        UserProfile.objects.create(user=kwargs.get('instance'))

post_save.connect(create_profile, sender=User)
