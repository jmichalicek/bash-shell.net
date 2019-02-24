from django.views.generic.dates import ArchiveIndexView

from .models import BlogPage


class PostArchiveView(ArchiveIndexView):
    """
    Post archive by year, month

    Technically could be a wagtail Page model now, but I didn't want to make a model for just this one page.
    """
    model = BlogPage
    date_field = 'first_published_at'
    template_name = 'blog/post_archive.html'
