# TODO: wagtail factory_boy factory stuff.

import factory
import wagtail_factories

from bash_shell_net.blog.models import BlogPage, BlogPageIndex


class BlogPageIndexFactory(wagtail_factories.PageFactory):
    title = "Blog"

    class Meta:
        model = BlogPageIndex


class BlogPageFactory(wagtail_factories.PageFactory):

    title = factory.Sequence(lambda n: f"Blog Post {n}")

    class Meta:
        model = BlogPage
