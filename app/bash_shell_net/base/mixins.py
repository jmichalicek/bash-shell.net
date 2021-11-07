"""
Reusable mixins - possibly should be its own app/package, but leaving in base for now.
"""
import inspect
from typing import List, Type

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


class IdAndSlugUrlIndexMixin:
    """
    Mixin for wagtail index pages using RoutablePageMixin to provide a url route which has the Page id and slug in the url.

    The page is looked up by the id and if the slug does not match, the user is redirected to the url with the
    correct slug to allow urls to continue to work if a slug gets changed.
    """

    # TODO: Test cases for this - probably need to make a tests dir, test/models.py, and then settings/tests.py
    # which includes the blog.tests app so that these models get loaded.
    # For now, these are tested indirectly because I have written tests for the models which use these mixins.

    # I don't like duplicating this on IdAndSlugUrlMixin.  Maybe that can optionally take a IdAndSlugUrlIndexMixin parent class?
    id_and_slug_url_name = ''
    id_and_slug_url_class = None

    def get_id_and_slug_url_name(self) -> str:
        """
        Returns the name of the id_and_slug url route
        """
        return self.id_and_slug_url_name

    def get_id_and_slug_url_class(self) -> type:
        """
        Returns the class specified by self.get_id_and_slug_url_class

        This works with both:
            id_and_slug_url_class = MyClass
            id_and_slug_url_class = 'myapp.models.MyClass'
        """
        if inspect.isclass(self.id_and_slug_url_class):
            return self.id_and_slug_url_class
        return import_string(self.id_and_slug_url_class)

    def page_by_id_and_slug(self, request, id, slug, *args, **kwargs) -> HttpResponse:
        """
        Look up page using the a "slug" which is really the post id followed by the actual slug
        """
        # TODO: Is there a way to include this on IdAndSlugUrlIndexMixin with the decorator? Or maybe I duplicate
        # or call the decorator from within IdAndSlugUrlIndexMixin.__init__()
        # TODO: I am using this pattern in several places, make it more generic/reusable even if not on the mixin
        page = self.get_id_and_slug_url_class().objects.filter(pk=id)
        if not getattr(request, 'is_preview', False):
            page = page.live()
        page = page.first()
        if not page:
            raise Http404
        if not page.slug == slug:
            # using this for efficiency vs page.get_id_and_slug_url()
            # TODO: review wagtail docs to see if there is a simple and efficient way to have it just default
            # to the id and slug url for page.url
            return HttpResponseRedirect(
                self.url + self.reverse_subpage(self.get_id_and_slug_url_name(), kwargs={'id': id, 'slug': page.slug})
            )
        # or return blog_page.serve(request, *args, **kwargs) ??
        return page.serve(request, *args, **kwargs)


class IdAndSlugUrlMixin:
    """
    A mixin for wagtail Page models for detail pages with a url route which has the Page id and slug in the url.

    The custom route is expected to be on a parent index page using RoutablePageMixin and works along with IdAndSlugUrlIndexMixin.
    """

    # TODO: Test cases for this - probably need to make a tests dir, test/models.py, and then settings/tests.py
    # which includes the blog.tests app so that these models get loaded.
    # For now, these are tested indirectly because I have written tests for the models which use these mixins.

    id_and_slug_url_name = ''

    @cached_property
    def id_and_slug_url(self) -> str:
        # tempted to just put this in actual cache instead, but that feels dirty on a model even though this model
        # is really more akin to a django view
        return self.get_id_and_slug_url()

    def get_id_and_slug_url_name(self) -> str:
        """
        Returns the name of the id_and_slug url route
        """
        if not self.id_and_slug_url_name:
            # parent_page check is because maybe the parent does not use IdAndSlugUrlIndexMixin or implement that itself
            # but only if we do not have a set name on our class so that unnecessary db lookup can be avoided
            # Could use a property and then a classmethod on IdAndSlugUrlIndexMixin completely avoiding any
            # db lookups, but I feel like I'm overengineering to solve a performance problem which does not yet exist.
            parent_page = self.get_parent().specific
            if hasattr(parent_page, 'get_id_and_slug_url_name'):
                return parent_page.get_id_and_slug_url_name()
        return self.id_and_slug_url_name

    def get_id_and_slug_url(self) -> str:
        """
        Returns the url path for on_tap_recipe_by_id_and_slug route
        """
        # lightly modified from https://github.com/wagtail/wagtail/blob/ba6f94def17b8bbc66002cbc7af60ed422658ff1/wagtail/contrib/routable_page/templatetags/wagtailroutablepage_tags.py#L10
        parent = self.get_parent().specific
        base_url = parent.relative_url(self.get_site())
        routed_url = parent.reverse_subpage(self.get_id_and_slug_url_name(), kwargs={'id': self.pk, 'slug': self.slug})
        if not base_url.endswith('/'):
            base_url += '/'
        return base_url + routed_url

    def get_full_id_and_slug_url(self, request) -> str:
        """
        Return the full id and slug URL (including protocol / domain) to this page, or None if it is not routable

        Could also override get_url_parts() to return this url instead of the default one.
        """
        url_parts = self.get_url_parts(request=request)

        if url_parts is None or url_parts[1] is None and url_parts[2] is None:
            # page is not routable
            return

        site_id, root_url, page_path = url_parts

        return root_url + self.id_and_slug_url

    def get_sitemap_urls(self, request=None) -> list[dict]:
        """
        Returns url for the sitemap using the full id_and_slug_url instead of wagtail default full_url()
        """
        return [
            {
                'location': self.get_full_id_and_slug_url(request=request),
                # fall back on latest_revision_created_at if last_published_at is null
                # (for backwards compatibility from before last_published_at was added)
                'lastmod': (self.last_published_at or self.latest_revision_created_at),
            }
        ]
