# This all needs fixed for wagtail
from django.contrib.syndication.views import Feed

from bash_shell_net.blog.models import BlogPage


class BlogFeedRss(Feed):
    """RSS feed of latest posts"""

    title = "Bash-Shell.Net Posts"
    link = "/"
    description = "Latest bash-shell.net posts"

    def items(self):
        return BlogPage.objects.live().order_by("-first_published_at")[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        # This might go wrong.  HTML might show up in here
        # seems to be ok so far even though some things I read suggested
        # html in the rss could be bad
        # TODO: almost definitely needs updated for wagtail
        return "%s..." % (item.body[:250])

    def item_link(self, item):
        return item.id_and_slug_url
