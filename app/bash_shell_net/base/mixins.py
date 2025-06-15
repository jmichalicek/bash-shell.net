"""
Reusable mixins - possibly should be its own app/package, but leaving in base for now.
"""

from typing import Any, Protocol

from django.http import Http404, HttpResponse, HttpResponseRedirect

from wagtail.models import Page


class WagtailPage(Protocol):
    pk: Any

    def get_url_parts(self, *args, **kwargs) -> tuple[int, str, str]: ...


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
    id_and_slug_url_name: str = ""

    def get_id_and_slug_url_name(self) -> str:
        """
        Returns the name of the id_and_slug url route
        """
        return self.id_and_slug_url_name

    def child_page_by_id_and_slug(self, request, id, slug, *args, **kwargs) -> HttpResponse:
        """
        Look up page using the "slug" which is really the post id followed by the actual slug
        """
        # TODO: Is there a way to include this on IdAndSlugUrlIndexMixin with the decorator? Or maybe I duplicate
        # or call the decorator from within IdAndSlugUrlIndexMixin.__init__()
        # TODO: I am using this pattern in several places, make it more generic/reusable even if not on the mixin
        assert isinstance(self, Page)
        page = self.children().filter(pk=id)
        if not getattr(request, "is_preview", False):
            page = page.live()
        page = page.first()
        if not page:
            raise Http404
        if not page.slug == slug:
            # TODO: review wagtail docs to see if there is a simple and efficient way to have it just default
            # to the id and slug url for page.url
            return HttpResponseRedirect(
                self.url + self.reverse_subpage(self.get_id_and_slug_url_name(), kwargs={"id": id, "slug": page.slug})
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

    def get_url_parts(self: WagtailPage, *args, **kwargs) -> tuple[int, str, str]:
        site_id, root_url, page_path = super().get_url_parts(*args, **kwargs)  # type: ignore [safe-super]
        path_parts = page_path.split("/")
        path_parts.insert(-2, str(self.pk))
        # path_parts has leading and trailing empty strings which results in
        # this getting the intended leading and trailing slashes.
        page_path = "/".join(path_parts)
        return site_id, root_url, page_path
