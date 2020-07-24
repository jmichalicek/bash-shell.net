from wagtail.tests.utils import WagtailPageTests

from django.test import TestCase
import unittest

from ..models import *

from wagtail.tests.utils.form_data import nested_form_data, rich_text, streamfield, inline_formset


class PageTreeTest(WagtailPageTests):
    """
    Test things like where pages can be created
    """

    def test_page_tree(self):
        self.assertCanCreateAt(RecipeIndexPage, RecipePage)
        self.assertAllowedSubpageTypes(RecipeIndexPage, [RecipePage])


class RecipePageTest(WagtailPageTests):
    """
    Test the RecipePage
    """

    fixtures = ['on_tap/fixtures/test_pages.json']

    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_color_srm(self):
        pass

    def test_can_create_page(self):
        recipe_page_index = RecipeIndexPage.objects.first()
        # Assert that a ContentPage can be made here, with this POST data
        x = nested_form_data(
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
        print(x)
        self.assertCanCreate(recipe_page_index, RecipePage, x)


class RecipeIndexPageTest(WagtailPageTests):
    pass


class BatchLogPageTest(WagtailPageTests):
    pass


class BatchLogIndexPageTest(WagtailPageTests):
    pass


class RecipeFermentableTest(TestCase):
    @unittest.skip('Skipped because I have not written this but at least I will see skipped tests now.')
    def test_calculate_mcu(self):
        pass
