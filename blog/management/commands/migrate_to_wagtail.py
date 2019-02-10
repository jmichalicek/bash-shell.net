"""
Migrate the last few years of blog app Post model to wagtail.
"""

from django.core.management.base import BaseCommand
from ...models import Post, BlogPost  # going to rename this BlogPage I think
import markdown
from django.conf import settings


class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        for p in Post.objects.all().order_by('id'):
            wagtail_post = BlogPost.objects.create(slug=p.slug, title=p.title, owner=p.user)
            # TODO: figure out how to get post body in here from p.content, which is markdown
            post_content = markdown.markdown(p.content, output_format='html5', extensions=settings.MARKDOWN_EXTENSIONS)

            # TODO: make sure it's in a published state.
            BlogPost.objects.filter(id=wagtail_post.id).update(first_published_at=p.published_date)
