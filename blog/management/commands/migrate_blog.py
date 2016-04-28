from __future__ import print_function, unicode_literals, absolute_import
"""
Migrate the old bsblog data to the new blog app
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

class Command(BaseCommand):
    ...
    can_import_settings = True

    def handle(self, *args, **options):
        from ...models import *
        from bsblog.models import Category, Post as OldPost

        # migrate categories to tags
        for category in Category.objects.all():
            try:
                Tag.objects.get(name__iexact=category.name.strip())
            except Tag.DoesNotExist:
                Tag.objects.create(name=category.name.strip())

        for old_post in OldPost.objects.all().order_by('id'):
            if Post.objects.filter(slug=old_post.slug).exists():
                print("Skipping post id ", old_post.id, " with slug [", old_post.slug, "] due to existing new post with slug")
                continue
            post = Post.objects.create(
                title=old_post.title,
                content=old_post.text_html,
                slug=old_post.slug,
                is_published=old_post.published,
                user_profile=old_post.user_profile
            )
            if post.is_published:
                post.published_date = old_post.created_date

            post.tags = [old_post.category]
            Post.objects.filter(id=post.id).update(created_date=old_post.created_date, updated_date=old_post.created_date)
