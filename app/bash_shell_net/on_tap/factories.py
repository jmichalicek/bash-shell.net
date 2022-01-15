from decimal import Decimal

import factory
import wagtail_factories

from bash_shell_net.on_tap.models import (
    BatchLogIndexPage,
    BatchLogPage,
    BeverageStyle,
    OnTapPage,
    RecipeIndexPage,
    RecipePage,
)


class BeverageStyleFactory(factory.django.DjangoModelFactory):

    name = "English Porter"
    style_guide = "BJCP"
    category = "Brown British Beer"
    category_number = 13
    style_letter = "C"
    beverage_type = "ale"
    original_gravity_min = Decimal("1.040")
    original_gravity_max = Decimal("1.052")
    final_gravity_min = Decimal("1.008")
    final_gravity_max = Decimal("1.014")
    ibu_min = Decimal("18.00")
    ibu_max = Decimal("35.00")
    color_min = Decimal("20.00")
    color_max = Decimal("30.00")
    abv_min = Decimal("4.00")
    abv_max = Decimal("5.40")
    notes = ""
    external_url = ""

    class Meta:
        model = BeverageStyle
        django_get_or_create = ('name', 'style_guide', 'category', 'category_number')


class OnTapPageFactory(wagtail_factories.PageFactory):

    title = 'On Tap'

    class Meta:
        model = OnTapPage


class BatchLogIndexPageFactory(wagtail_factories.PageFactory):

    title = 'Batch Logs'

    class Meta:
        model = BatchLogIndexPage


class BatchLogPageFactory(wagtail_factories.PageFactory):

    title = factory.Sequence(lambda n: 'Batch %n')

    class Meta:
        model = BatchLogPage


class RecipeIndexPageFactory(wagtail_factories.PageFactory):

    title = 'Recipes'

    class Meta:
        model = RecipeIndexPage


class RecipePageFactory(wagtail_factories.PageFactory):

    title = factory.Sequence(lambda n: 'Recipe %n')
    # TODO: get rid of name
    name = factory.Sequence(lambda n: 'Recipe %n')
    recipe_type = "all_grain"
    # this does not quite play correctly because of the order things are created and validated by wagtail
    style = factory.SubFactory(BeverageStyleFactory)
    brewer = "Justin Michalicek"
    assistant_brewer = ""
    volume_units = "gal"
    batch_size = Decimal("2.50")
    boil_size = Decimal("3.60")
    boil_time = 60
    efficiency = 75
    boil_gravity = None
    original_gravity = Decimal("1.050")
    final_gravity = Decimal("1.013")
    ibus_tinseth = Decimal("25.00")

    class Meta:
        model = RecipePage
