from django.contrib.syndication.views import Feed
from django.utils import timezone

from blog.models import *

class BlogFeedRss(Feed):
    """RSS feed of latest posts"""
    title = "Bash-Shell.Net Posts"
    link = "/"
    description = "Latest bash-shell.net posts"

    def items(self):
        return Post.objects.filter(
            is_published=True, published_date__lte=timezone.now
        ).order_by('-published_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self,item):
        # This might go wrong.  HTML might show up in here
        # seems to be ok so far even though some things I read suggested
        # html in the css could be bad
        return u'%s...' %(item.content[:250])
