from __future__ import unicode_literals, absolute_import, division

from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Post


class PostListView(ListView):
    """
    List of published posts
    """
    model = Post
    queryset = Post.objects.all() #.select_related('user')
    paginate_by = 15
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        queryset = super(PostListView, self).get_queryset()
        queryset = queryset.filter(published_date__isnull=False,
                                   published_date__lte=timezone.now())
        queryset = queryset.prefetch_related('tags')
        return queryset


class PostDetailView(DetailView):
    """
    Public view of a single Post
    """
    model = Post
    queryset = Post.objects.all() #  .select_related('user')
    template_name = 'blog/post_detail.html'

    def get_queryset(self):
        queryset = super(PostDetailView, self).get_queryset()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_published=True,
                                       published_date__isnull=False,
                                       published_date__lte=timezone.now())

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context.update({
            'tags': self.object.tags.all()
        })
        return context
