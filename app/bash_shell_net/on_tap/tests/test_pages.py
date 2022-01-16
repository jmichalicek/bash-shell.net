import copy
import unittest
from decimal import Decimal
from urllib.parse import urlencode

from django.test import RequestFactory, TestCase

from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import inline_formset, nested_form_data, rich_text, streamfield

from bash_shell_net.base.test_utils import add_wagtail_factory_page
from bash_shell_net.on_tap.factories import (
    BatchLogIndexPageFactory,
    BatchLogPageFactory,
    OnTapPageFactory,
    RecipeIndexPageFactory,
    RecipePageFactory,
    create_default_recipe_page,
)
from bash_shell_net.on_tap.models import (
    BatchLogIndexPage,
    BatchLogPage,
    BeverageStyle,
    OnTapPage,
    RecipeIndexPage,
    RecipePage,
    VolumeUnit,
)

DATE_FORMAT = '%B %d, %Y'

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
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.on_tap_page: OnTapPage = add_wagtail_factory_page(OnTapPageFactory)
        cls.recipe_index_page = add_wagtail_factory_page(RecipeIndexPageFactory, parent_page=cls.on_tap_page)
        cls.recipe_page = add_wagtail_factory_page(RecipePageFactory, parent_page=cls.recipe_index_page)
        cls.batch_log_index_page = add_wagtail_factory_page(BatchLogIndexPageFactory, parent_page=cls.on_tap_page)

    def test_get_request_no_batches(self):
        """
        Test an HTTP GET request to a published OnTapPage with no published batches.
        """
        r = self.client.get(self.on_tap_page.url)
        self.assertEqual(r.status_code, 200)
        self.assertQuerysetEqual(r.context['currently_on_tap'], [])
        self.assertQuerysetEqual(r.context['upcoming_batches'], [])
        self.assertQuerysetEqual(r.context['past_batches'], [])
        self.assertTrue('page_obj' in r.context)
        self.assertTrue('paginator' in r.context)

    def test_get_request_with_batches(self):
        """
        Test an HTTP GET request to a published OnTapPage with no published batches.
        """

        on_tap_batch = add_wagtail_factory_page(
            BatchLogPageFactory,
            parent_page=self.batch_log_index_page,
            slug='on-tap-batch',
            brewed_date='2020-07-10',
            packaged_date='2020-07-25',
            on_tap_date='2020-07-25',
            status='complete',
            recipe_page=self.recipe_page,
        )

        planned_batch = add_wagtail_factory_page(
            BatchLogPageFactory,
            parent_page=self.batch_log_index_page,
            slug='planned-batch',
            status='planned',
            recipe_page=self.recipe_page,
        )

        fermenting_batch = add_wagtail_factory_page(
            BatchLogPageFactory,
            parent_page=self.batch_log_index_page,
            slug='fermenting-batch',
            status='fermenting',
            brewed_date='2020-06-10',
            recipe_page=self.recipe_page,
        )

        previous_batch = add_wagtail_factory_page(
            BatchLogPageFactory,
            parent_page=self.batch_log_index_page,
            brewed_date='2020-06-10',
            packaged_date='2020-06-25',
            on_tap_date='2020-06-25',
            off_tap_date='2020-07-25',
            status='complete',
            recipe_page=self.recipe_page,
        )

        page = self.on_tap_page

        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(list(r.context['currently_on_tap']), [on_tap_batch])
        self.assertEqual(list(r.context['upcoming_batches']), [fermenting_batch, planned_batch])
        self.assertEqual(list(r.context['past_batches']), [previous_batch])
        self.assertTrue('page_obj' in r.context)
        self.assertTrue('paginator' in r.context)

        with self.subTest(scaled_recipe=False):
            # TODO: Test the whole block of html for this which would allow verifying that it's in the right place?
            expected_on_tap_batches = f'''
                <div class="col-md-4 col-12 mt-3 mt-md-0 pr-0">
                    <div class="card currently-on-tap">
                        <div class="card-header text-center">
                            <div class="w-100"><a href="{on_tap_batch.recipe_page.id_and_slug_url}">{on_tap_batch.recipe_page.name}</a></div>
                            <small>{on_tap_batch.recipe_page.style.name} ({on_tap_batch.recipe_page.style.bjcp_category()})</small>
                        </div>
                        <div class="card-body">
                            <p class="card-text">{on_tap_batch.recipe_page.short_description}</p>
                            <p class="card-text">On Tap {on_tap_batch.on_tap_date.strftime('%B %d, %Y')}</p>
                        </div>
                        <div class="card-footer">
                            <a href="{on_tap_batch.id_and_slug_url}" class="card-link">Details</a>
                        </div>
                    </div>
                </div>
            '''

            expected_coming_soon_batches = f'''
            <tbody>
                <tr>
                <td>
                    <a href="{fermenting_batch.recipe_page.id_and_slug_url}">{fermenting_batch.recipe_page.name}</a>
                    (<a href="{fermenting_batch.id_and_slug_url}">Log</a>)
                </td>
                <td>{fermenting_batch.recipe_page.style}</td>
                <td>{fermenting_batch.get_status_display()}</td>
                <td>{fermenting_batch.brewed_date.strftime(DATE_FORMAT)}</td>
                <td></td>
                <td></td>
                </tr>
                <tr>
                <td>
                    <a href="{planned_batch.recipe_page.id_and_slug_url}">{planned_batch.recipe_page.name}</a>
                </td>
                <td>{planned_batch.recipe_page.style}</td>
                <td>{planned_batch.get_status_display()}</td>
                <td></td>
                <td></td>
                <td></td>
                </tr>
            </tbody>
            '''
            self.assertInHTML(expected_on_tap_batches, r.content.decode('utf-8'))
            self.assertInHTML(expected_coming_soon_batches, r.content.decode('utf-8'))

        # now test the html with a scaled recipe
        for b in [on_tap_batch, fermenting_batch, planned_batch]:
            b.target_post_boil_volume = b.recipe_page.batch_size * 2
            b.save_revision()
            publish_page(b)
            b.refresh_from_db()

        r = self.client.get(page.url)

        with self.subTest(scaled_recipe=True):
            expected_on_tap_batches = f'''
                <div class="col-md-4 col-12 mt-3 mt-md-0 pr-0">
                    <div class="card currently-on-tap">
                        <div class="card-header text-center">
                            <div class="w-100"><a href="{on_tap_batch.recipe_page.id_and_slug_url}?scale_volume={on_tap_batch.target_post_boil_volume}&scale_unit={on_tap_batch.volume_units}">{on_tap_batch.recipe_page.name}</a></div>
                            <small>{on_tap_batch.recipe_page.style.name} ({on_tap_batch.recipe_page.style.bjcp_category()})</small>
                        </div>
                        <div class="card-body">
                            <p class="card-text">{on_tap_batch.recipe_page.short_description}</p>
                            <p class="card-text">On Tap {on_tap_batch.on_tap_date.strftime(DATE_FORMAT)}</p>
                        </div>
                        <div class="card-footer">
                            <a href="{on_tap_batch.id_and_slug_url}" class="card-link">Details</a>
                        </div>
                    </div>
                </div>
            '''

            expected_coming_soon_batches = f'''
            <tbody>
                <tr>
                <td>
                    <a href="{fermenting_batch.recipe_page.id_and_slug_url}?scale_volume={fermenting_batch.target_post_boil_volume}&amp;scale_unit={fermenting_batch.volume_units}">{fermenting_batch.recipe_page.name}</a>
                    (<a href="{fermenting_batch.id_and_slug_url}">Log</a>)
                </td>
                <td>{fermenting_batch.recipe_page.style}</td>
                <td>{fermenting_batch.get_status_display()}</td>
                <td>{fermenting_batch.brewed_date.strftime(DATE_FORMAT)}</td>
                <td></td>
                <td></td>
                </tr>
                <tr>
                <td>
                    <a href="{planned_batch.recipe_page.id_and_slug_url}?scale_volume={planned_batch.target_post_boil_volume}&amp;scale_unit={planned_batch.volume_units}">{planned_batch.recipe_page.name}</a>
                </td>
                <td>{planned_batch.recipe_page.style}</td>
                <td>{planned_batch.get_status_display()}</td>
                <td></td>
                <td></td>
                <td></td>
                </tr>
            </tbody>
            '''

            self.assertInHTML(expected_on_tap_batches, r.content.decode('utf-8'))
            self.assertInHTML(expected_coming_soon_batches, r.content.decode('utf-8'))


class RecipePageTest(WagtailPageTests):
    """
    Test the RecipePage
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        on_tap_page: OnTapPage = add_wagtail_factory_page(OnTapPageFactory)
        cls.recipe_index_page: RecipeIndexPage = add_wagtail_factory_page(
            RecipeIndexPageFactory, parent_page=on_tap_page
        )
        cls.recipe_page: RecipePage = add_wagtail_factory_page(RecipePageFactory, parent_page=cls.recipe_index_page)
        cls.beverage_style: BeverageStyle = cls.recipe_page.style

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        # Otherwise I get weird errors
        # see https://github.com/jmichalicek/bash-shell.net/commit/928bbd2d35e92aaca293ab0873dd5001c79c80e1#diff-ca9c96ccc066402806c6ad539615860324119d2bb9550592df76f0e803e8ee59R233
        self.recipe_index_page.refresh_from_db()
        self.recipe_page.refresh_from_db()

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
                "style": self.beverage_style.pk,
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
                "conclusion": streamfield(
                    [
                        ("paragraph", rich_text("<p>Recipe conclusion.</p>")),
                    ],
                ),
                "hops": inline_formset([]),
                "yeasts": inline_formset([]),
                "fermentables": inline_formset([]),
                "miscellaneous_ingredients": inline_formset([]),
            },
        )
        self.assertCanCreate(self.recipe_index_page, RecipePage, form_data)
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
        self.assertEqual(f'{self.recipe_index_page.get_url()}{page.pk}/{page.slug}/', page.get_id_and_slug_url())

    def test_request_by_id_and_slug_route(self):
        # Technically a method/route on RecipePageIndex but it is to route to this model... :shrug:
        page = self.recipe_page
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

        url = page.get_id_and_slug_url()
        url = f'{url[:-1]}1/'
        r = self.client.get(url)
        self.assertRedirects(
            r,
            page.get_id_and_slug_url(),
        )

    def test_scale_to_volume(self):
        """
        Test that recipe_page.scale_to_volume() scales all measurements for itself up to the specified volume
        """
        # need to modify the copy here. It seems the self.recipe_page.refresh_from_db() does not reset
        # the relationships/managers for the reverse foreign keys
        scaled_recipe = copy.copy(self.recipe_page)
        scaled_recipe.scale_to_volume(
            target_volume=scaled_recipe.batch_size * Decimal('2.00'), unit=VolumeUnit(scaled_recipe.volume_units)
        )
        self.assertEqual(self.recipe_page.batch_size * 2, scaled_recipe.batch_size)
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.fermentables.all()],
            [{f.pk: f.amount} for f in scaled_recipe.fermentables.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.hops.all()],
            [{f.pk: f.amount} for f in scaled_recipe.hops.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.miscellaneous_ingredients.all()],
            [{f.pk: f.amount} for f in scaled_recipe.miscellaneous_ingredients.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.yeasts.all()],
            [{f.pk: f.amount} for f in scaled_recipe.yeasts.all()],
        )

    def test_get_scaled_recipe(self):
        """
        Test that recipe_page.get_scaled_recipe() returns a new instance of RecipePage which has been scaled to the specified volume
        """
        scaled_recipe = self.recipe_page.get_scaled_recipe(
            target_volume=self.recipe_page.batch_size * Decimal('2.00'), unit=VolumeUnit(self.recipe_page.volume_units)
        )
        self.assertEqual(self.recipe_page.pk, scaled_recipe.pk)
        self.assertFalse(self.recipe_page is scaled_recipe)
        self.assertEqual(self.recipe_page.batch_size * 2, scaled_recipe.batch_size)
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.fermentables.all()],
            [{f.pk: f.amount} for f in scaled_recipe.fermentables.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.hops.all()],
            [{f.pk: f.amount} for f in scaled_recipe.hops.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.miscellaneous_ingredients.all()],
            [{f.pk: f.amount} for f in scaled_recipe.miscellaneous_ingredients.all()],
        )
        self.assertEqual(
            [{f.pk: f.amount * 2} for f in self.recipe_page.yeasts.all()],
            [{f.pk: f.amount} for f in scaled_recipe.yeasts.all()],
        )


class RecipeIndexPageTest(WagtailPageTests):
    def test_get_request(self):
        """
        Test a GET request to the RecipeIndexPage
        """
        on_tap_page: OnTapPage = add_wagtail_factory_page(OnTapPageFactory)
        recipe_index_page: RecipeIndexPage = add_wagtail_factory_page(RecipeIndexPageFactory, parent_page=on_tap_page)

        r = self.client.get(recipe_index_page.url)
        self.assertEqual(r.status_code, 200)


class BatchLogIndexPageTest(WagtailPageTests):
    def test_get_request(self):
        """
        Test a GET request to the BatchLogIndexPage
        """
        on_tap_page: OnTapPage = add_wagtail_factory_page(OnTapPageFactory)
        batch_log_index_page: BatchLogIndexPage = add_wagtail_factory_page(
            BatchLogIndexPageFactory, parent_page=on_tap_page
        )
        r = self.client.get(batch_log_index_page.url)
        self.assertEqual(r.status_code, 200)


class BatchLogPageTest(WagtailPageTests):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        on_tap_page: OnTapPage = add_wagtail_factory_page(OnTapPageFactory)
        cls.recipe_index_page: RecipeIndexPage = add_wagtail_factory_page(
            RecipeIndexPageFactory, parent_page=on_tap_page
        )
        # cls.recipe_page: RecipePage = add_wagtail_factory_page(RecipePageFactory, parent_page=cls.recipe_index_page)
        cls.recipe_page = cls.recipe_index_page.add_child(instance=create_default_recipe_page())
        cls.batch_log_index_page: BatchLogIndexPage = add_wagtail_factory_page(
            BatchLogIndexPageFactory, parent_page=on_tap_page
        )
        cls.batch_log_page = add_wagtail_factory_page(
            BatchLogPageFactory,
            parent_page=cls.batch_log_index_page,
            slug='on-tap-batch',
            status='planned',
            recipe_page=cls.recipe_page,
            final_gravity=Decimal("0"),
        )

    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()
        # MUST refresh recipe_page before batch_log_page or things go weird and there are
        # completely random, intermittent failures due to incorrect db data
        self.recipe_page.refresh_from_db()
        self.batch_log_page.refresh_from_db()
        # This test is very strange and randomly fails with the following exception.
        # The actual test which fails from it is random. I now believe that it may be if there was a
        # test failure in the previous run, both using --keepdb, then something is not rolled back properly.
        """
        Traceback (most recent call last):
            File "/django/bash-shell.net/app/bash_shell_net/on_tap/tests/test_pages.py", line 475, in setUp
                self.batch_log_page.refresh_from_db()
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/base.py", line 650, in refresh_from_db
                db_instance = db_instance_qs.get()
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/query.py", line 431, in get
                num = len(clone)
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/query.py", line 262, in __len__
                self._fetch_all()
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/query.py", line 1324, in _fetch_all
                self._result_cache = list(self._iterable_class(self))
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/query.py", line 47, in __iter__
                db = queryset.db
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/models/query.py", line 1254, in db
                return self._db or router.db_for_read(self.model, **self._hints)
            File "/django/bash-shell.net/app/.venv/lib/python3.10/site-packages/django/db/utils.py", line 250, in _route_db
                if instance is not None and instance._state.db:
            AttributeError: 'StreamValue' object has no attribute 'db'
        """

    def test_get_request(self):
        """
        Test a GET request to the default url and validate rendered html
        """

        # unscaled
        r = self.client.get(self.batch_log_page.full_url)
        self.assertEqual(200, r.status_code)
        # todo: tests for brewed, packaged, on tap, etc to validate those dates are in correctly
        expected_basic_details_html = f'''
        <div class="card row">
          <div class="card-body">
            <ul class="list-unstyled">
              <li>Brewed: N/A</li>
              <li>Packaged: N/A</li>
              <li>On Tap: N/A</li>
              <li>Recipe: <a href="{self.batch_log_page.recipe_page.id_and_slug_url}">{self.batch_log_page.recipe_page.name}</a></li>
            </ul>
          </div>
        </div>
        '''
        self.assertInHTML(expected_basic_details_html, r.content.decode('utf-8'))

        # test scaled
        self.batch_log_page.target_post_boil_volume = self.batch_log_page.recipe_page.batch_size * 2
        self.batch_log_page.save()
        r = self.client.get(self.batch_log_page.full_url)
        expected_basic_details_html = f'''
        <div class="card row">
          <div class="card-body">
            <ul class="list-unstyled">
              <li>Brewed: N/A</li>
              <li>Packaged: N/A</li>
              <li>On Tap: N/A</li>
              <li>Recipe: <a href="{self.batch_log_page.recipe_page.id_and_slug_url}?scale_volume={self.batch_log_page.target_post_boil_volume}&scale_unit={self.batch_log_page.volume_units}">{self.batch_log_page.recipe_page.name}</a></li>
            </ul>
          </div>
        </div>
        '''
        self.assertInHTML(expected_basic_details_html, r.content.decode('utf-8'))

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
                'body': streamfield(
                    [
                        (
                            "paragraph",
                            rich_text("<p>This is a test recipe.</p>"),
                        )
                    ]
                ),
                'volume_in_fermenter': 2.75,
                'volume_units': 'gal',
                'target_post_boil_volume': '',
            },
        )
        self.assertCanCreate(self.batch_log_index_page, BatchLogPage, form_data)
        page = BatchLogPage.objects.filter(slug='test-case-batch').first()
        publish_page(page)
        page.refresh_from_db()
        r = self.client.get(page.url)
        self.assertEqual(r.status_code, 200)

    def test_request_by_id_and_slug_route(self):
        # Technically a method/route on BatchLogPageIndex but it is to route to this model... :shrug:
        page = self.batch_log_page
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

        url = page.get_id_and_slug_url()
        url = f'{url[:-1]}1/'
        r = self.client.get(url)
        self.assertRedirects(
            r,
            page.get_id_and_slug_url(),
        )

    def test_get_id_and_slug_url(self):
        """
        Test that BatchLogPage.get_id_and_slug_url() returns the url route we expect.
        """
        # page = BatchLogPage.objects.first()
        page = self.batch_log_page
        self.assertEqual(f'{self.batch_log_index_page.get_url()}{page.pk}/{page.slug}/', page.get_id_and_slug_url())

    def test_fermenter_volume_as_gallons(self):
        expected_conversion = {
            VolumeUnit.GALLON: Decimal(1),
            VolumeUnit.FLUID_OZ: Decimal('0.0078125'),
            VolumeUnit.QUART: Decimal('0.25'),
            VolumeUnit.LITER: Decimal('0.26417287'),
        }
        # page = BatchLogPage.objects.first()
        page = self.batch_log_page
        base_volume = Decimal('2.75')
        for unit in [VolumeUnit.GALLON, VolumeUnit.FLUID_OZ, VolumeUnit.QUART, VolumeUnit.LITER]:
            page.volume_in_fermenter = Decimal(2.75) / expected_conversion[unit]
            page.volume_units = unit.value
            with self.subTest(volume_units=page.get_volume_units_display(), volume=page.volume_in_fermenter):
                self.assertEqual(base_volume, page.fermenter_volume_as_gallons().quantize(base_volume))

    def test_post_boil_volume_as_gallons(self):
        expected_conversion = {
            VolumeUnit.GALLON: Decimal(1),
            VolumeUnit.FLUID_OZ: Decimal('0.0078125'),
            VolumeUnit.QUART: Decimal('0.25'),
            VolumeUnit.LITER: Decimal('0.26417287'),
        }
        # page = BatchLogPage.objects.first()
        page = self.batch_log_page
        base_volume = Decimal('2.75')
        for unit in [VolumeUnit.GALLON, VolumeUnit.FLUID_OZ, VolumeUnit.QUART, VolumeUnit.LITER]:
            page.post_boil_volume = Decimal(2.75) / expected_conversion[unit]
            page.volume_units = unit.value
            with self.subTest(volume_units=page.get_volume_units_display(), volume=page.volume_in_fermenter):
                self.assertEqual(base_volume, page.post_boil_volume_as_gallons().quantize(base_volume))

    def test_calculate_color_srm(self):
        page = self.batch_log_page
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
        # page = BatchLogPage.objects.first()
        page = self.batch_log_page
        # page.post_boil_volume = None  # do I care?
        # page.save()
        test_matrix = [
            {'volume': None, 'expected_srm': 26, 'target_post_boil_volume': None},  # the recipe srm
            {'volume': Decimal('2.75'), 'expected_srm': 24, 'target_post_boil_volume': None},
            # Everything scaled evenly, so srm should match the recipe expected srm
            {'volume': Decimal('5.00'), 'expected_srm': 26, 'target_post_boil_volume': Decimal('5.00')},
            {'volume': Decimal('3.00'), 'expected_srm': 23, 'target_post_boil_volume': None},
            {'volume': Decimal('5.00'), 'expected_srm': 16, 'target_post_boil_volume': None},
        ]
        for t in test_matrix:
            page.post_boil_volume = t['volume']
            page.target_post_boil_volume = t['target_post_boil_volume']
            with self.subTest(**t):
                self.assertEqual(t['expected_srm'], page.get_actual_or_expected_srm())

        # add test for a scaled recipe

    def test_uses_scaled_recipe(self):
        page = self.batch_log_page
        test_matrix = [
            {
                'target_post_boil_volume': None,
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('gal'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': False,
            },
            {
                'target_post_boil_volume': Decimal(2.5),
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('gal'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': False,
            },
            {
                'target_post_boil_volume': Decimal(2.5),
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('fl_oz'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': True,
            },
            {
                'target_post_boil_volume': Decimal(2.6),
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('gal'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': True,
            },
        ]

        for t in test_matrix:
            page.target_post_boil_volume = t['target_post_boil_volume']
            page.volume_units = t['batch_volume_units']
            page.recipe_page.batch_size = t['batch_size']
            page.recipe_page.volume_units = t['recipe_volume_units']
            with self.subTest(**t):
                self.assertEqual(t['expected'], page.uses_scaled_recipe)

    def test_get_abv(self):
        page = self.batch_log_page
        test_matrix = [
            {'final_gravity': Decimal('1.010'), 'original_gravity': Decimal('1.050'), 'expected_abv': Decimal('5.250')},
            {
                'final_gravity': Decimal('1.010'),
                'original_gravity': Decimal('1.060'),
                'expected_abv': Decimal('6.56250'),
            },
            {
                'final_gravity': Decimal('1.015'),
                'original_gravity': Decimal('1.050'),
                'expected_abv': Decimal('4.59375'),
            },
        ]
        for t in test_matrix:
            page.final_gravity = t['final_gravity']
            page.original_gravity = t['original_gravity']
            with self.subTest(**t):
                self.assertEqual(t['expected_abv'], page.get_abv())

    def test_get_context(self):
        request = self.request_factory.get(self.batch_log_page.url)
        test_matrix = [
            # scaled recipe
            {
                'target_post_boil_volume': Decimal(2.6),
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('gal'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': True,
            },
            # not scaled recipe
            {
                'target_post_boil_volume': None,
                'batch_size': Decimal(2.5),
                'batch_volume_units': VolumeUnit('gal'),
                'recipe_volume_units': VolumeUnit('gal'),
                'expected': True,
            },
        ]

        for t in test_matrix:
            self.batch_log_page.target_post_boil_volume = t['target_post_boil_volume']
            self.batch_log_page.volume_units = t['batch_volume_units']
            self.batch_log_page.recipe_page.batch_size = t['batch_size']
            self.batch_log_page.recipe_page.volume_units = t['recipe_volume_units']
            with self.subTest(**t):
                context = self.batch_log_page.get_context(request=request)
                self.assertEqual(self.batch_log_page.get_actual_or_expected_srm(), context['calculated_srm'])
                self.assertEqual(self.batch_log_page.recipe_page, context['recipe_page'])

    def test_recipe_url(self):
        """
        Test that the recipe_url property returns the url for the recipe page without scaling querystring parameters.
        """
        self.assertEqual(self.batch_log_page.recipe_page.id_and_slug_url, self.batch_log_page.recipe_url)

    def test_recipe_url_scaled(self):
        """
        Test that the recipe url for a batch which has been scaled differently from the original recipe
        contains scaling querystring parameters.
        """
        self.batch_log_page.target_post_boil_volume = self.batch_log_page.recipe_page.batch_size * 2
        self.batch_log_page.save()

        expected_url = self.batch_log_page.recipe_page.id_and_slug_url
        query_params = urlencode(
            {
                'scale_volume': self.batch_log_page.target_post_boil_volume,
                'scale_unit': self.batch_log_page.volume_units,
            }
        )
        expected_url = f'{expected_url}?{query_params}'
        self.assertEqual(expected_url, self.batch_log_page.recipe_url)


class RecipeFermentableTest(TestCase):
    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_mcu(self):
        pass
