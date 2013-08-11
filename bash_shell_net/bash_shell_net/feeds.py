from django.contrib.syndication.views import Feed
from bsblog.models import *

class BlogFeedRss(Feed):
    """RSS feed of latest posts"""
    title = "Bash-Shell.Net Posts"
    link = "/"
    description = "Latest bash-shell.net posts"

    def items(self):
        return Post.objects.order_by('-created_date')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self,item):
        # This might go wrong.  HTML might show up in here
        # seems to be ok so far even though some things I read suggested
        # html in the css could be bad
        return u'%s...' %(item.text_html[:250])
