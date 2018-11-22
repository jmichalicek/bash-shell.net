from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.dates import ArchiveIndexView

from .models import Post


class PostListView(ListView):
    """
    List of published posts
    """
    model = Post
    queryset = Post.objects.all().select_related('user')
    paginate_by = 15
    template_name = 'blog/post_list.html'
    ordering = '-published_date'

    def get_queryset(self):
        queryset = super(PostListView, self).get_queryset()
        queryset = queryset.filter(published_date__isnull=False, published_date__lte=timezone.now())
        queryset = queryset.prefetch_related('tags')
        return queryset.order_by('-published_date')


class PostDetailView(DetailView):
    """
    Public view of a single Post
    """
    model = Post
    queryset = Post.objects.all().select_related('user')
    template_name = 'blog/post_detail.html'

    def get_queryset(self):
        queryset = super(PostDetailView, self).get_queryset()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_published=True, published_date__isnull=False,
                                       published_date__lte=timezone.now())

        return queryset

    def get_context_data(self, **kwargs):
        tags = self.object.tags.all()

        previous_post_q = Q(published_date=self.object.published_date, id__lt=self.object.id)
        previous_post_q = previous_post_q | Q(published_date__lt=self.object.published_date)
        previous_post = Post.objects.published().filter(previous_post_q).exclude(pk=self.object.pk).order_by(
            '-published_date', 'id').first()

        next_post_q = Q(published_date=self.object.published_date, id__gt=self.object.id)
        next_post_q = next_post_q | Q(published_date__gt=self.object.published_date)
        next_post = Post.objects.published().filter(next_post_q).exclude(pk=self.object.pk).order_by(
            'published_date', '-id').first()

        return super(PostDetailView, self).get_context_data(next_post=next_post, previous_post=previous_post, tags=tags,
                                                            **kwargs)


class PostArchiveView(ArchiveIndexView):
    """
    Post archive by year, month
    """
    model = Post
    date_field = 'published_date'
    template_name = 'blog/post_archive.html'


class PostPreviewView(LoginRequiredMixin, DetailView):
    """
    Preview a post as a logged in user.
    """
    model = Post
    queryset = Post.objects.all().select_related('user')
    template_name = 'blog/post_detail.html'

    def handle_no_permission(self):
        raise Http404()
