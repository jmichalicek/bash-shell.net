from decimal import Decimal
from typing import Any

import factory
import wagtail_factories

from bash_shell_net.on_tap.models import (
    BatchLogIndexPage,
    BatchLogPage,
    BatchOnTapRecord,
    BeverageStyle,
    OnTapPage,
    RecipeFermentable,
    RecipeHop,
    RecipeIndexPage,
    RecipePage,
    RecipeYeast,
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
        django_get_or_create = ("name", "style_guide", "category", "category_number")


class OnTapPageFactory(wagtail_factories.PageFactory):

    title = "On Tap"

    class Meta:
        model = OnTapPage


class BatchLogIndexPageFactory(wagtail_factories.PageFactory):

    title = "Batch Logs"

    class Meta:
        model = BatchLogIndexPage


class BatchLogPageFactory(wagtail_factories.PageFactory):

    title = factory.Sequence(lambda n: f"Batch {n}")
    recipe_page = factory.SubFactory("bash_shell_net.on_tap.factories.RecipePageFactory")  # type:ignore[var-annotated]
    body = wagtail_factories.StreamFieldFactory({"0": wagtail_factories.CharBlockFactory})  # type:ignore[var-annotated]
    volume_units: Any = factory.SelfAttribute("recipe_page.volume_units")
    target_post_boil_volume: Any = factory.SelfAttribute("recipe_page.batch_size")
    post_boil_volume: Any = factory.SelfAttribute("target_post_boil_volume")
    volume_in_fermenter: Any = factory.LazyAttribute(lambda o: o.recipe_page.batch_size - Decimal("0.25"))

    class Meta:
        model = BatchLogPage

    class Params:
        on_tap: factory.Trait = factory.Trait(
            on_tap_records=factory.RelatedFactory(
                "bash_shell_net.on_tap.factories.BatchOnTapRecordFactory",
                factory_related_name="batch_log_page",
                on_tap=True,
            )
        )
        off_tap: factory.Trait = factory.Trait(
            on_tap_records=factory.RelatedFactory(
                "bash_shell_net.on_tap.factories.BatchOnTapRecordFactory",
                factory_related_name="batch_log_page",
                off_tap=True,
            )
        )


class RecipeIndexPageFactory(wagtail_factories.PageFactory):

    title = "Recipes"

    class Meta:
        model = RecipeIndexPage


class RecipeFermentableFactory(factory.django.DjangoModelFactory):
    recipe_page = factory.SubFactory("bash_shell_net.on_tap.factories.RecipePageFactory")  # type:ignore[var-annotated]
    amount = Decimal("3.600")
    amount_units = "lb"
    name = "Maris Otter"
    type = "grain"
    color = Decimal("3.000")

    class Meta:
        model = RecipeFermentable


class RecipeHopFactory(factory.django.DjangoModelFactory):
    recipe_page = factory.SubFactory("bash_shell_net.on_tap.factories.RecipePageFactory")  # type:ignore[var-annotated]
    name = "Fuggles"
    alpha_acid_percent = Decimal("5.000")
    amount = Decimal("0.70")
    amount_units = "oz"
    use_step = "boil"
    use_time = 60
    form = "pellet"

    class Meta:
        model = RecipeHop


class RecipePageFactory(wagtail_factories.PageFactory):

    title = factory.Sequence(lambda n: f"Recipe {n}")
    recipe_type = "all_grain"
    style = factory.SubFactory(BeverageStyleFactory)  # type:ignore[var-annotated]
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
    introduction = wagtail_factories.StreamFieldFactory({"0": wagtail_factories.CharBlockFactory()})
    conclusion = wagtail_factories.StreamFieldFactory({"0": wagtail_factories.CharBlockFactory()})

    class Meta:
        model = RecipePage

    @classmethod
    def _build(cls, model_class, *args, **kwargs) -> RecipePage:
        # factory.post_generation AND factory.SubFactory both seem to save the BeverageStyle after wagtail
        # has done its model validation, resulting in exceptions being raised due to missing the style
        if not (beverage_style := kwargs.get("style")):
            beverage_style = BeverageStyleFactory.build()
            kwargs.update({"style": beverage_style})

        if not beverage_style.pk:
            beverage_style.save()

        return super()._build(model_class, *args, **kwargs)


class RecipeYeastFactory(factory.django.DjangoModelFactory):
    recipe_page = factory.SubFactory("bash_shell_net.on_tap.factories.RecipePageFactory")  # type:ignore[var-annotated]
    name = "SafAle S-04"
    amount = Decimal("0.388")
    amount_units = "oz"
    add_to_secondary = False
    yeast_type = "dry"

    class Meta:
        model = RecipeYeast


def create_default_recipe_page() -> RecipePage:
    recipe = RecipePageFactory.build()
    recipe.hops = [RecipeHopFactory.build(recipe_page=recipe)]

    recipe.fermentables = [
        # default is maris otter. May turn these all into traits
        RecipeFermentableFactory.build(
            maltster="William Crisp",
        ),
        RecipeFermentableFactory.build(
            amount=Decimal("8.00"),
            amount_units="oz",
            name="Crisp Brown Malt",
            type="grain",
            color=Decimal("85.000"),
            maltster="William Crisp",
        ),
        RecipeFermentableFactory.build(
            amount=Decimal("5.00"),
            amount_units="oz",
            name="Caramel 40",
            type="grain",
            color=Decimal("40.000"),
            maltster="Briess",
        ),
        RecipeFermentableFactory.build(
            amount=Decimal("3.00"),
            amount_units="oz",
            name="Caramel 80",
            type="grain",
            color=Decimal("80.000"),
            maltster="Briess",
        ),
        RecipeFermentableFactory.build(
            amount=Decimal("2.00"),
            amount_units="oz",
            name="Chocolate Malt",
            type="grain",
            color=Decimal("450.000"),
            maltster="William Crisp",
        ),
        RecipeFermentableFactory.build(
            amount=Decimal("1.500"),
            amount_units="oz",
            name="Pale Chocolate Malt",
            type="grain",
            color=Decimal("225.000"),
            maltster="William Crisp",
        ),
    ]

    recipe.yeasts = [RecipeYeastFactory.build()]
    return recipe


class BatchOnTapRecordFactory(factory.django.DjangoModelFactory):
    batch_log_page: factory.SubFactory = factory.SubFactory(BatchLogPageFactory)

    class Meta:
        model = BatchOnTapRecord

    class Params:
        on_tap: factory.Trait = factory.Trait(on_tap_date=factory.Faker("past_date", start_date="-2y"))
        off_tap: factory.Trait = factory.Trait(
            on_tap=True, off_tap_date=factory.Faker("past_date", start_date=factory.SelfAttribute("..on_tap_date"))
        )
