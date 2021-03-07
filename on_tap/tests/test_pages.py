import unittest

from django.test import TestCase

from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import inline_formset, nested_form_data, rich_text, streamfield

from ..models import *
from ..models import VolumeToGallonsConverter

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
    # TODO: factories, not fixtures
    fixtures = ['on_tap/fixtures/test_pages']

    @classmethod
    def setUpTestData(cls):
        cls.on_tap_page = OnTapPage.objects.first()
        cls.batch_log_index_page = BatchLogIndexPage.objects.first()
        cls.batch_log_page = BatchLogPage.objects.first()
        cls.recipe_index_page = RecipeIndexPage.objects.first()
        cls.recipe_page = RecipePage.objects.first()

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
                'volume_units': 'gal',
            },
        )
        if not batch_index_page:
            batch_index_page = self.batch_log_index_page
        self.assertCanCreate(batch_index_page, BatchLogPage, form_data)
        page = BatchLogPage.objects.get(slug=slug)
        return page

    def test_get_request_with_batches(self):
        """
        Test an HTTP GET request to a published OnTapPage with no published batches.
        """
        for p in RecipePage.objects.all():
            publish_page(p)

        batch_index = self.batch_log_index_page
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

        page = self.on_tap_page
        publish_page(page)
        page.refresh_from_db()

        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(list(r.context['currently_on_tap']), [on_tap_batch])
        self.assertEqual(list(r.context['upcoming_batches']), [fermenting_batch, planned_batch, self.batch_log_page])
        self.assertEqual(list(r.context['past_batches']), [previous_batch])
        self.assertTrue('page_obj' in r.context)
        self.assertTrue('paginator' in r.context)


class RecipePageTest(WagtailPageTests):
    """
    Test the RecipePage
    """

    fixtures = ['on_tap/fixtures/test_pages']

    @classmethod
    def setUpTestData(cls):
        cls.index_page = RecipeIndexPage.objects.first()
        # TODO: Confirm that RoutablePageMixin routes only work when the RoutablePage is published.
        # Not certain yet, but that seems to be behavior I have seen.
        publish_page(cls.index_page)
        cls.recipe_page = RecipePage.objects.first()

    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_color_srm(self):
        pass

    def test_can_create_page(self):
        """
        Test creating a RecipePage under the RecipeIndexPage via form with expected data creates the page.
        """
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
        self.assertCanCreate(self.index_page, RecipePage, form_data)
        page = RecipePage.objects.filter(slug='test-case-recipe').first()
        publish_page(page)
        page.refresh_from_db()
        # Not 100% certain this is a super useful test with wagtail
        # but I think it is since it'll run through the page's get_context(), template logic, etc.
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)

    def test_get_id_and_slug_url(self):
        """
        Test that RecipePage.get_id_and_slug_url() returns the url route we expect.
        """
        page = self.recipe_page
        # /on-tap/recipes/<pk>/<slug>/
        self.assertEqual(f'{self.index_page.get_url()}{page.pk}/{page.slug}/', page.get_id_and_slug_url())

    def test_request_by_id_and_slug_route(self):
        # Technically a method/route on RecipePageIndex but it is to route to this model... :shrug:
        page = self.recipe_page
        publish_page(page)
        r = self.client.get(page.get_id_and_slug_url())
        self.assertEqual(200, r.status_code)
        # TODO: test that we got the expected page - maybe add in a 2nd published page to be 100% certain

    def test_request_by_id_and_slug_route_redirects_on_slug_mismatch(self):
        """
        Test that a GET request to the id_and_slug_url redirects to the correct slug if the requested slug does not
        match the current slug.
        """
        # Technically a method/route on BatchLogPageIndex but it is to route to this model... :shrug:
        page = self.recipe_page
        publish_page(page)

        url = page.get_id_and_slug_url()
        url = f'{url[:-1]}1/'
        r = self.client.get(url)
        self.assertRedirects(
            r, page.get_id_and_slug_url(),
        )


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

    @classmethod
    def setUpTestData(cls):
        cls.index_page = BatchLogIndexPage.objects.first()
        publish_page(cls.index_page)
        cls.recipe_page = RecipePage.objects.first()
        publish_page(cls.recipe_page)
        cls.batch_log_page = BatchLogPage.objects.first()

    def test_can_create_page(self):
        """
        Test creating a BatchLogPage under the BatchLogIndexPage via form with expected data creates the page.
        """
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
                'recipe_page': self.recipe_page.pk,
                'brewed_date': '2020-07-10',
                'packaged_date': '2020-07-25',
                'on_tap_date': '2020-07-25',
                'off_tap_date': '',
                'original_gravity': 1.050,
                'final_gravity': 1.016,
                'status': 'complete',
                'body': streamfield([("paragraph", rich_text("<p>This is a test recipe.</p>"),)]),
                'volume_in_fermenter': 2.75,
                'volume_units': 'gal',
            },
        )
        self.assertCanCreate(self.index_page, BatchLogPage, form_data)
        page = BatchLogPage.objects.filter(slug='test-case-batch').first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)

    def test_request_by_id_and_slug_route(self):
        # Technically a method/route on BatchLogPageIndex but it is to route to this model... :shrug:
        page = self.batch_log_page
        # just make it published? Or have two pages for testing both published and unpublished page stuff?
        publish_page(page)
        r = self.client.get(page.get_id_and_slug_url())
        self.assertEqual(200, r.status_code)
        # TODO: test that we got the expected page - maybe add in a 2nd published page to be 100% certain

    def test_request_by_id_and_slug_route_redirects_on_slug_mismatch(self):
        """
        Test that a GET request to the id_and_slug_url redirects to the correct slug if the requested slug does not
        match the current slug.
        """
        # Technically a method/route on BatchLogPageIndex but it is to route to this model... :shrug:
        page = self.batch_log_page
        publish_page(page)

        url = page.get_id_and_slug_url()
        url = f'{url[:-1]}1/'
        r = self.client.get(url)
        self.assertRedirects(
            r, page.get_id_and_slug_url(),
        )

    def test_get_id_and_slug_url(self):
        """
        Test that BatchLogPage.get_id_and_slug_url() returns the url route we expect.
        """
        page = BatchLogPage.objects.first()
        self.assertEqual(f'{self.index_page.get_url()}{page.pk}/{page.slug}/', page.get_id_and_slug_url())

    def test_fermenter_volume_as_gallons(self):
        expected_conversion = {
            VolumeUnit.GALLON: Decimal(1),
            VolumeUnit.FLUID_OZ: Decimal('0.0078125'),
            VolumeUnit.QUART: Decimal('0.25'),
            VolumeUnit.LITER: Decimal('0.26417287'),

        }
        page = BatchLogPage.objects.first()
        base_volume = Decimal('2.75')
        for unit in [VolumeUnit.GALLON, VolumeUnit.FLUID_OZ, VolumeUnit.QUART, VolumeUnit.LITER]:
            page.volume_in_fermenter = Decimal(2.75 ) / expected_conversion[unit]
            page.volume_units = unit.value
            with self.subTest(volume_units=page.get_volume_units_display(), volume=page.volume_in_fermenter):
                self.assertEqual(base_volume, page.fermenter_volume_as_gallons().quantize(base_volume))

    def test_post_boil_volume_in_gallons(self):
        expected_conversion = {
            VolumeUnit.GALLON: Decimal(1),
            VolumeUnit.FLUID_OZ: Decimal('0.0078125'),
            VolumeUnit.QUART: Decimal('0.25'),
            VolumeUnit.LITER: Decimal('0.26417287'),

        }
        page = BatchLogPage.objects.first()
        base_volume = Decimal('2.75')
        for unit in [VolumeUnit.GALLON, VolumeUnit.FLUID_OZ, VolumeUnit.QUART, VolumeUnit.LITER]:
            page.post_boil_volume = Decimal(2.75 ) / expected_conversion[unit]
            page.volume_units = unit.value
            with self.subTest(volume_units=page.get_volume_units_display(), volume=page.volume_in_fermenter):
                self.assertEqual(base_volume, page.post_boil_volume_as_gallons().quantize(base_volume))

    def test_calculate_color_srm(self):
        page = BatchLogPage.objects.first()
        test_matrix = [
            {'volume': Decimal('2.75'), 'expected_srm': 24},
            {'volume': Decimal('3.00'), 'expected_srm': 23},
            {'volume': Decimal('5.00'), 'expected_srm': 16},
        ]
        for t in test_matrix:
            page.post_boil_volume = Decimal(t['volume'])
            with self.subTest(volume=page.post_boil_volume):
                self.assertEqual(Decimal(t['expected_srm']), page.calculate_color_srm())

    def test_get_actual_or_expected_srm(self):
        page = BatchLogPage.objects.first()
        page.post_boil_volume = None
        page.save()
        test_matrix = [
            {'volume': None, 'expected_srm': 26},  # the recipe srm
            {'volume': Decimal('2.75'), 'expected_srm': 24},
            {'volume': Decimal('3.00'), 'expected_srm': 23},
            {'volume': Decimal('5.00'), 'expected_srm': 16},
        ]
        for t in test_matrix:
            page.post_boil_volume = t['volume']
            with self.subTest(volume=page.post_boil_volume):
                self.assertEqual(t['expected_srm'], page.get_actual_or_expected_srm())



class RecipeFermentableTest(TestCase):
    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_mcu(self):
        pass
