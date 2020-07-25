from wagtail.tests.utils import WagtailPageTests
from wagtail.core.models import Page

from django.test import TestCase
import unittest

from ..models import *

from wagtail.tests.utils.form_data import nested_form_data, rich_text, streamfield, inline_formset

# TODO: These tests are a bit slow, I suspect due to creating pages and then publishing them separately
# rather than just creating already published pages. Will sort this out when I implement factory_boy
# for these pages.


def publish_page(page: Page) -> None:
    """
    Publish the latest revision of a page
    """
    revision = page.revisions.latest('id')
    revision.publish()


class PageTreeTest(WagtailPageTests):
    """
    Test things like where pages can be created
    """

    def test_page_tree(self):
        self.assertCanCreateAt(RecipeIndexPage, RecipePage)
        self.assertAllowedSubpageTypes(RecipeIndexPage, [RecipePage])
        self.assertCanCreateAt(BatchLogIndexPage, BatchLogPage)
        self.assertAllowedSubpageTypes(BatchLogIndexPage, [BatchLogPage])


class OnTapPageTest(WagtailPageTests):
    fixtures = ['on_tap/fixtures/test_pages']

    def test_get_request_no_batches(self):
        """
        Test an HTTP GET request to a published OnTapPage with no published batches.
        """
        page = OnTapPage.objects.first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)
        self.assertQuerysetEqual(r.context['currently_on_tap'], [])
        self.assertQuerysetEqual(r.context['upcoming_batches'], [])
        self.assertQuerysetEqual(r.context['past_batches'], [])
        self.assertTrue('page_obj' in r.context)
        self.assertTrue('paginator' in r.context)

    def _make_batch_log_page(self, slug: str, batch_index_page: BatchLogIndexPage = None, **kwargs) -> BatchLogPage:
        # FACTORIES!!!!!
        status = kwargs.get('status', 'planned')
        brewed_date = kwargs.get('brewed_date', '')
        packaged_date = kwargs.get('packaged_date', '')
        on_tap_date = kwargs.get('on_tap_date', '')
        off_tap_date = kwargs.get('off_tap_date', '')
        status = kwargs.get('status', '')
        recipe_page = kwargs.get('recipe_page', RecipePage.objects.live().first())

        form_data = nested_form_data(
            {
                'title': slug,
                'slug': slug,
                'seo_title': '',
                'search_description': '',
                'go_live_at': '',
                'expire_at': '',
                'name': 'Brewing The Test Case Recipe',
                'recipe_page': recipe_page.pk,
                'brewed_date': brewed_date,
                'packaged_date': packaged_date,
                'on_tap_date': on_tap_date,
                'off_tap_date': off_tap_date,
                'original_gravity': 1.050,
                'final_gravity': 1.016,
                'status': status,
                'body': streamfield([("paragraph", rich_text("<p>This is a test recipe.</p>"),)]),
            },
        )
        if not batch_index_page:
            batch_index_page = RecipeIndexPage.objects.latest('id')
        self.assertCanCreate(batch_index_page, BatchLogPage, form_data)
        page = BatchLogPage.objects.get(slug=slug)
        return page

    def test_get_request_with_batches(self):
        """
        Test an HTTP GET request to a published OnTapPage with no published batches.
        """
        for p in RecipePage.objects.all():
            publish_page(p)

        batch_index = BatchLogIndexPage.objects.first()
        publish_page(batch_index)

        on_tap_batch = self._make_batch_log_page(
            slug='on-tap-batch',
            batch_index_page=batch_index,
            brewed_date='2020-07-10',
            packaged_date='2020-07-25',
            on_tap_date='2020-07-25',
            status='complete',
        )
        planned_batch = self._make_batch_log_page(slug='planned-batch', batch_index_page=batch_index, status='planned')
        fermenting_batch = self._make_batch_log_page(
            slug='fermenting-batch', batch_index_page=batch_index, status='fermenting', brewed_date='2020-06-10',
        )
        previous_batch = self._make_batch_log_page(
            slug='off-tap-batch',
            batch_index_page=batch_index,
            brewed_date='2020-06-10',
            packaged_date='2020-06-25',
            on_tap_date='2020-06-25',
            off_tap_date='2020-07-25',
            status='complete',
        )

        for p in BatchLogPage.objects.all():
            publish_page(p)

        page = OnTapPage.objects.first()
        publish_page(page)
        page.refresh_from_db()

        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(list(r.context['currently_on_tap']), [on_tap_batch])
        self.assertEqual(list(r.context['upcoming_batches']), [fermenting_batch, planned_batch])
        self.assertEqual(list(r.context['past_batches']), [previous_batch])
        self.assertTrue('page_obj' in r.context)
        self.assertTrue('paginator' in r.context)


class RecipePageTest(WagtailPageTests):
    """
    Test the RecipePage
    """

    fixtures = ['on_tap/fixtures/test_pages']

    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_color_srm(self):
        pass

    def test_can_create_page(self):
        """
        Test creating a RecipePage under the RecipeIndexPage via form with expected data creates the page.
        """
        recipe_page_index = RecipeIndexPage.objects.first()
        # Assert that a ContentPage can be made here, with this POST data
        # TODO: More tests - one with minimum post data one with everything.
        form_data = nested_form_data(
            {
                'title': 'Test Case Recipe',
                'slug': 'test-case-recipe',
                'seo_title': '',
                'search_description': '',
                'go_live_at': '',
                'expire_at': '',
                'name': 'Test Case Recipe',
                "short_description": "Test Recipe",
                "recipe_type": "all_grain",
                "style": 1,
                "brewer": "Justin Michalicek",
                "assistant_brewer": "",
                "volume_units": "gal",
                "batch_size": "2.50",
                "boil_size": "3.50",
                "boil_time": 60,
                "efficiency": 74,
                "boil_gravity": "",
                "original_gravity": "1.048",
                "final_gravity": "1.012",
                "ibus_tinseth": "25.00",
                "notes": "null",  # yep, "null". jsondecodeerror if not and this is also what firefox sends in real form submissions
                "introduction": streamfield(
                    [
                        (
                            "paragraph",
                            rich_text(
                                "<p>This is a test recipe. The numbers for it are not correct because this is not actually the real grains and hops used.</p>"
                            ),
                        )
                    ]
                ),
                "conclusion": streamfield([("paragraph", rich_text("<p>Recipe conclusion.</p>")),],),
                "hops": inline_formset([]),
                "yeasts": inline_formset([]),
                "fermentables": inline_formset([]),
                "miscellaneous_ingredients": inline_formset([]),
            },
        )
        self.assertCanCreate(recipe_page_index, RecipePage, form_data)
        page = RecipePage.objects.filter(slug='test-case-recipe').first()
        publish_page(page)
        page.refresh_from_db()
        # Not 100% certain this is a super useful test with wagtail
        # but I think it is since it'll run through the page's get_context(), template logic, etc.
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)


class RecipeIndexPageTest(WagtailPageTests):
    fixtures = ['on_tap/fixtures/test_pages']

    def test_get_request(self):
        """
        Test a GET request to the RecipeIndexPage
        """
        page = RecipeIndexPage.objects.first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)


class BatchLogIndexPageTest(WagtailPageTests):
    fixtures = ['on_tap/fixtures/test_pages']

    def test_get_request(self):
        """
        Test a GET request to the BatchLogIndexPage
        """
        page = BatchLogIndexPage.objects.first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)


class BatchLogPageTest(WagtailPageTests):
    fixtures = ['on_tap/fixtures/test_pages']

    def test_can_create_page(self):
        """
        Test creating a BatchLogPage under the BatchLogIndexPage via form with expected data creates the page.
        """
        index_page = BatchLogIndexPage.objects.first()
        recipe_page = RecipePage.objects.first()
        # TODO: More tests - one with minimum post data one with everything.
        form_data = nested_form_data(
            {
                'title': 'Test Case Batch',
                'slug': 'test-case-batch',
                'seo_title': '',
                'search_description': '',
                'go_live_at': '',
                'expire_at': '',
                'name': 'Brewing The Test Case Recipe',
                'recipe_page': recipe_page.pk,
                'brewed_date': '2020-07-10',
                'packaged_date': '2020-07-25',
                'on_tap_date': '2020-07-25',
                'off_tap_date': '',
                'original_gravity': 1.050,
                'final_gravity': 1.016,
                'status': 'complete',
                'body': streamfield([("paragraph", rich_text("<p>This is a test recipe.</p>"),)]),
            },
        )
        self.assertCanCreate(index_page, BatchLogPage, form_data)
        page = BatchLogPage.objects.filter(slug='test-case-batch').first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)


class RecipeFermentableTest(TestCase):
    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_mcu(self):
        pass
