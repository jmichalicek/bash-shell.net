from wagtail.models import Page, Site

import wagtail_factories


def add_wagtail_factory_page(
    page_factory: wagtail_factories.PageFactory, parent_page: Page | None = None, **kwargs
) -> Page:
    """
    Uses a page factory to add a page as a child of the specified parent page. If no parent page
    is specified then the default site's root page is used. If no default site exists then one is created.
    """
    if not parent_page:
        if not (site := Site.objects.filter(is_default_site=True).first()):
            site = wagtail_factories.SiteFactory(is_default_site=True)
        parent_page = site.root_page

    page: Page = parent_page.add_child(instance=page_factory.build(**kwargs))
    return page
