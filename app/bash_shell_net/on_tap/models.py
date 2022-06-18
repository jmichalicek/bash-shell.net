import copy
from decimal import Decimal
from enum import Enum
from typing import Any
from urllib.parse import urlencode

from django.contrib.postgres.fields import CICharField
from django.core.paginator import EmptyPage
from django.core.paginator import Page as PaginatorPage
from django.core.paginator import PageNotAnInteger, Paginator
from django.db import models
from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.safestring import mark_safe

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, create_deferring_foreign_related_manager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from bash_shell_net.base.mixins import IdAndSlugUrlIndexMixin, IdAndSlugUrlMixin
from bash_shell_net.on_tap.forms import BatchLogPageForm
from bash_shell_net.wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS


class VolumeToGallonsConverter(Enum):
    """
    Multipliers to convert from other volume units to gallons.

    Multiply other volumes times these to convert to gallons. 4 quarts = 1 gallon, so multiple quarts by 0.25, etc.
    """

    # TODO: Similarly to VolumeUnit, making this a models.Choices subclass like
    # VolumeToGallonsConverter(decimal.Decimal, models.Choices):
    # might be a good idea.
    GALLON = Decimal(1)
    FLUID_OZ = Decimal('0.0078125')
    QUART = Decimal('0.25')
    LITER = Decimal('0.26417287')


class WeightUnits(models.TextChoices):
    GRAMS = 'g', 'Gram'
    OUNCES = 'oz', 'Ounce'
    POUNDS = 'lbs', 'Pound'
    KILOGRAMS = 'kg', 'Kilogram'


class VolumeUnits(models.TextChoices):
    TEASPOON = 'tsp', 'Teaspoon'
    TABLESPOON = 'tbsp', 'Tablespoon'
    FLUID_OUNCE = 'fl_oz', 'Fluid Oz'
    LITER = 'l', 'Liter'
    QUART = 'quart'
    GALLON = 'gal', 'Gallon'


class RecipeType:
    """
    The type of beer recipe
    """

    # or just use ints and enum this?
    ALL_GRAIN = 'all_grain'
    EXTRACT = 'extract'
    PARTIAL_MASH = 'partial_mash'


class VolumeUnit(Enum):
    # TODO: Django's models.TextChoices would be great here.
    FLUID_OZ = 'fl_oz'
    LITER = 'l'
    GALLON = 'gal'
    QUART = 'quart'


def convert_volume_to_gallons(volume: Decimal, unit: VolumeUnit) -> Decimal:
    """
    Converts the batch volume to gallons for use in SRM estimation using Morey's equation
    """
    # Probably makes sense to live on either VolumeUnit or VolumeToGallonsConverter now.
    return volume * VolumeToGallonsConverter[unit.name].value


class ScalableAmountMixin:
    """
    Allows having a property `amount` and an optional `scaled_amount` property. Keeps the values in sync
    by using `__setattr__()`
    """

    # This can also be implemented with `__getattribute__()` checking for `scaled_amount` and returning it
    # whenever `amount` is called for, which works in read only situations, but if `scaled_amount` does exist
    # then things get wonky saving forms.

    def __setattr__(self, name, value):
        if name == 'scaled_amount':
            # using super() instead of self.<attr> to avoid infinite loop alternating between these two
            super().__setattr__('amount', value)
        elif name == 'amount':
            super().__setattr__('scaled_amount', value)
        super().__setattr__(name, value)


class RecipePageTag(TaggedItemBase):
    content_object = ParentalKey("on_tap.RecipePage", on_delete=models.CASCADE, related_name="tagged_items")


class RecipeHop(ScalableAmountMixin, Orderable, models.Model):
    """
    A single amount of hops in a recipe
    """

    USE_STEP_CHOICES = (
        ('aroma', 'Aroma'),
        ('boil', 'Boil'),
        ('dryhop', 'Dry Hop'),
        ('firstwort', 'First Wort'),
        ('mash', 'Mash'),
    )

    FORM_CHOICES = (
        ('pellet', 'Pellet'),
        ('plug', 'Plug'),
        ('leaf', 'Leaf'),
    )

    TYPE_CHOICES = (
        ('bittering', 'Bittering'),
        ('aroma', 'Aroma'),
        ('both', 'Both'),
    )

    # Might FK this to a set of hops
    # would be good for name, type, substitutes, and origin
    recipe_page = ParentalKey(
        'on_tap.RecipePage',
        on_delete=models.CASCADE,
        related_name='hops',
        blank=False,
        null=False,
    )
    name = CICharField(max_length=100, blank=False)
    # A couple extra digits and decimal places to play it safe
    # Could also go FloatField and just be sure to round consistently
    alpha_acid_percent = models.DecimalField(max_digits=6, decimal_places=3, blank=False, null=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    amount_units = models.CharField(max_length=5, choices=(('g', 'Grams'), ('oz', 'Ounces')))
    # use_step maps to BeerXML <USE>
    use_step = models.CharField(choices=USE_STEP_CHOICES, max_length=15, blank=False)
    use_time = models.IntegerField(
        blank=False, null=False, help_text='Time in minutes. Specific meaning varies by use type.'
    )
    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )

    # type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    form = models.CharField(max_length=10, choices=FORM_CHOICES)
    beta_acid_percent = models.DecimalField(blank=True, default=None, max_digits=6, decimal_places=3, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('alpha_acid_percent'),
        FieldPanel('amount'),
        FieldPanel('amount_units'),
        FieldPanel('form'),
        FieldPanel('use_step'),
        FieldPanel('use_time'),
        FieldPanel('notes'),
        FieldPanel('beta_acid_percent'),
    ]

    class Meta:
        # sort_order is on Orderable
        ordering = ('recipe_page', 'sort_order')

    def __str__(self) -> str:
        return self.name

    def weight_in_ounces(self) -> Decimal:
        if self.amount_units == 'g':
            return self.amount * Decimal('0.035274')
        # for now, must be oz
        return self.amount


class RecipeFermentable(ScalableAmountMixin, Orderable, models.Model):
    """
    A fermentable such as a grain or malt extract used in a recipe

    The term "fermentable" encompasses all fermentable items that contribute substantially to the beer including
    extracts, grains, sugars, honey, fruits.
    """

    # TODO: usage? such as mash, vorlauf, or steep?

    UNIT_CHOICES = (
        ('g', 'Grams'),
        ('oz', 'Ounces'),
        ('kg', 'Kilograms'),
        ('lb', 'Pounds'),
    )

    TYPE_CHOICES = (
        ('grain', 'Grain'),
        ('dry_extract', 'Dry Extract'),
        ('liquid_extract', 'Liquid Extract'),
        ('sugar', 'Sugar'),
        ('adjunct', 'Adjunct'),
    )
    recipe_page = ParentalKey(
        'on_tap.RecipePage',
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name='fermentables',
    )
    amount = models.DecimalField(max_digits=6, decimal_places=3, blank=False, null=False)
    amount_units = models.CharField(
        max_length=5,
        blank=False,
        choices=UNIT_CHOICES,
    )
    # may add a static amount in kilograms to auto sort by amount
    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )

    # like hops, may be good FKd to a separate Fermentable with stats which don't change.
    # Name, Type, and Color belong on a separate Fermentable model, really.
    # there are many other stats which would be handy to keep on a separate model as well but are overkill here
    name = CICharField(max_length=100, blank=False)
    maltster = CICharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=25, choices=TYPE_CHOICES, blank=False)
    # TODO: Default these to 0 then can clean up null checking and rigging in self.calculate_mcu()
    color = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        blank=True,
        null=True,
        default=None,  # assuming sugars may have no Lovibond or SRM value
        help_text='The color of the item in Lovibond Units (SRM for liquid extracts).',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('maltster'),
        FieldPanel('amount'),
        FieldPanel('amount_units', heading='Units'),
        FieldPanel('color'),
        FieldPanel('type'),
        FieldPanel('notes'),
    ]

    class Meta:
        # sort_order is on Orderable
        ordering = ('recipe_page', 'sort_order')

    def __str__(self) -> str:
        return self.name

    def weight_in_pounds(self) -> Decimal:
        """
        Returns the weight in Pounds
        """
        # I should maybe just convert to oz or g on save, then return converted value as desired
        # that would also let me do things like use db sum() methods instead of iterating to get totals
        # Keep it dumb and simple for now
        if self.amount_units == 'kg':
            return self.amount * Decimal('2.20462262')
        elif self.amount_units == 'oz':
            return self.amount / Decimal('16.0')
        elif self.amount_units == 'g':
            # grams to kilograms then kilograms to pounds
            return (self.amount / Decimal('1000')) * Decimal('2.2042262')
        return self.amount

    def calculate_mcu(self, gallons: Decimal) -> Decimal:
        """
        Calculate the Malt Color Units for use in Morey's equation to calculate beer SRM.

        MCU is the weight of the grain in (pounds * color lovibond) / gallons
        """
        if gallons <= Decimal('0'):
            raise ValueError('gallons must be a positive number greater than 0')
        # Ensuring we have gallons as Decimal
        if self.color is None:
            color = Decimal(0)
        else:
            color = self.color
        return (self.weight_in_pounds() * color) / gallons


class RecipeYeast(ScalableAmountMixin, Orderable, models.Model):
    """
    A yeast used in a recipe.

    The term "yeast" encompasses all yeasts, including dry yeast, liquid yeast and yeast starters.

    Like RecipeHop and RecipeFermentable - a good candidate to have an FK back to a base Yeast
    """

    UNIT_CHOICES = (
        ('', '---------'),
        (
            'Weight',
            (
                ('g', 'Grams'),
                ('oz', 'Ounces'),
            ),
        ),
        (
            'Volume',
            (
                ('tsp', 'Teaspoons'),
                ('tbsp', 'Tablespoons'),
                ('fl_oz', 'Fluid Oz'),
                ('l', 'Liters'),
            ),
        ),
    )

    YEAST_TYPE_CHOICES = (
        ('dry', 'Dry'),
        ('liquid', 'Liquid'),
    )
    recipe_page = ParentalKey(
        'on_tap.RecipePage', on_delete=models.CASCADE, related_name='yeasts', blank=False, null=False
    )
    # like hops, may be good FKd to a separate Fermentable with stats which don't change.
    # name and many other details which I am not storing now
    # would be handy to keep on a separate model as well but are overkill here
    name = CICharField(max_length=100, blank=False)
    amount = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, default=None)
    amount_units = models.CharField(max_length=5, choices=UNIT_CHOICES, blank=True, default='')
    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )
    add_to_secondary = models.BooleanField(blank=True, default=False, null=False)
    yeast_type = models.CharField(max_length=25, choices=YEAST_TYPE_CHOICES, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # sort_order is on Orderable
        ordering = ('recipe_page', 'sort_order')

    def amount_is_weight(self) -> bool:
        return self.amount_units in ['g', 'oz']

    def __str__(self) -> str:
        return self.name


class RecipeMiscIngredient(ScalableAmountMixin, Orderable, models.Model):
    """
    The term "misc" encompasses all non-fermentable miscellaneous ingredients that are not hops or yeast and do not
    significantly change the gravity of the beer.  For example: spices, clarifying agents, water treatments, etc…

    Like RecipeHop and RecipeFermentable - a good candidate to have an FK back to a base Yeast
    """

    UNIT_CHOICES = (
        (
            'Weight',
            (
                ('g', 'Grams'),
                ('oz', 'Ounces'),
                ('kg', 'Kilograms'),
                ('lb', 'Pounds'),
            ),
        ),
        (
            'Volume',
            (
                ('tsp', 'Teaspoons'),
                ('tbsp', 'Tablespoons'),
                ('fl_oz', 'Fluid Oz.'),
                # cups?
                ('l', 'Liters'),
                ('gal', 'Gallons'),
            ),
        ),
    )

    TYPE_CHOICES = (
        ('spice', 'Spice'),
        ('fining', 'Fining'),
        ('water_agent', 'Water Agent'),
        ('herb', 'Herb'),
        ('flavor', 'Flavor'),
        ('other', 'Other'),
    )

    USE_STEP_CHOICES = (
        ('boil', 'Boil'),
        ('mash', 'Mash'),  # boil 'em, mash 'em, stick 'em in a stew.
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('bottling', 'Bottling'),
    )
    recipe_page = ParentalKey(
        'on_tap.RecipePage',
        on_delete=models.CASCADE,
        related_name='miscellaneous_ingredients',
        blank=False,
        null=False,
    )
    amount = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, default=None)
    amount_units = models.CharField(max_length=5, choices=UNIT_CHOICES, blank=False)
    use_time = models.IntegerField(
        blank=False, null=False, help_text='Amount of time the misc was boiled, steeped, mashed, etc in minutes.'
    )

    use_for = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
        help_text='Short description of what the ingredient is used for in text',
    )

    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
        help_text='Detailed notes on the item including usage. May be multiline.',
    )

    # Everything below here would likely be good on an FK'd MiscIngredient model
    # maybe use_step belongs per recipe?
    name = CICharField(max_length=100, blank=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, blank=False)
    use_step = models.CharField(max_length=20, choices=USE_STEP_CHOICES, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('type'),
        FieldPanel('amount'),
        FieldPanel('amount_units'),
        FieldPanel('use_step'),
        FieldPanel('use_time'),
        FieldPanel('use_for'),
        FieldPanel('notes'),
    ]

    class Meta:
        # sort_order is on Orderable
        ordering = ('recipe_page', 'sort_order')

    def __str__(self) -> str:
        return self.name


# Ignore type checking due to weird error with django 4.0.5, wagtail 3.0.1, mypy 0.961, django-stubs 1.12.0
# error: Couldn't resolve related manager for relation 'recipe_pages' (from bash_shell_net.on_tap.models.RecipePage.on_tap.RecipePage.style).
@register_snippet
class BeverageStyle(models.Model):  # type: ignore
    """
    http://www.beerxml.com/beerxml.htm

    <NAME>Dry Stout</NAME>
    <CATEGORY>Stout</CATEGORY>
    <CATEGORY_NUMBER>16</CATEGORY_NUMBER>
    <STYLE_LETTER>A</STYLE_LETTER>
    <STYLE_GUIDE>BJCP</STYLE_GUIDE>
    <VERSION>1</VERSION>
    <TYPE>Ale</TYPE>
    <OG_MIN>1.035</OG_MIN>
    <OG_MAX>1.050</OG_MAX>
    <FG_MIN>1.007</FG_MIN>
    <FG_MAX>1.011</FG_MAX>
    <IBU_MIN>30.0</IBU_MIN>
    <IBU_MAX>50.0</IBU_MAX>
    <COLOR_MIN>35.0</COLOR_MIN>
    <COLOR_MAX>200.0</COLOR_MAX>
    <ABV_MIN>3.2</ABV_MIN>
    <ABV_MAX>5.5</ABV_MAX>
    <CARB_MIN>1.6</CARB_MIN>
    <CARB_MAX>2.1</CARB_MAX>
    <NOTES>Famous Irish Stout.  Dry, roasted, almost coffee like flavor.  Often soured with pasteurized sour beer.  Full body perception due to flaked barley, though starting gravity may be low.  Dry roasted flavor.</NOTES>
    """

    template = 'on_tap/style_detail.html'
    TYPE_CHOICES = (
        ('ale', 'Ale'),
        ('lager', 'Lager'),
        ('cider', 'Cider'),
        ('mead', 'Mead'),
        ('mixed', 'Mixed'),
    )

    name = CICharField(max_length=50, blank=False)
    # Several of these are required by BeerXML but appear to be specific to BJCP and may not be part of
    # other style guides, such as AHA
    style_guide = models.CharField(max_length=50, blank=True, default='')
    category = models.CharField(max_length=100, blank=True, default='')
    category_number = models.SmallIntegerField(blank=True, null=True, default=None)
    style_letter = models.CharField(max_length=1, blank=True, default='')
    beverage_type = models.CharField(choices=TYPE_CHOICES, max_length=25, blank=True, default='', db_index=True)
    original_gravity_min = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=3)
    original_gravity_max = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=3)
    final_gravity_min = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=3)
    final_gravity_max = models.DecimalField(blank=True, null=True, default=None, max_digits=4, decimal_places=3)
    ibu_min = models.DecimalField(blank=True, null=True, default=None, max_digits=5, decimal_places=2)
    ibu_max = models.DecimalField(blank=True, null=True, default=None, max_digits=5, decimal_places=2)
    color_min = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Minimum SRM value'
    )
    color_max = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Maximum SRM value'
    )
    abv_min = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Minimum ABV %'
    )
    abv_max = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Maximum ABV %'
    )
    carbonation_min = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Minimum carbonation vol/vol'
    )
    carbonation_max = models.DecimalField(
        blank=True, null=True, default=None, max_digits=5, decimal_places=2, help_text='Maximum carbonation vol/vol'
    )
    notes = models.TextField(blank=True, default='')
    external_url = models.URLField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('external_url'),
        FieldPanel('beverage_type'),
        MultiFieldPanel(
            [
                FieldPanel('style_guide'),
                FieldPanel('category'),
                FieldPanel('category_number'),
                FieldPanel('style_letter'),
            ],
            heading='Style Guide Categorization',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('original_gravity_min'),
                FieldPanel('original_gravity_max'),
                FieldPanel('final_gravity_min'),
                FieldPanel('final_gravity_max'),
                FieldPanel('abv_min'),
                FieldPanel('abv_max'),
            ],
            heading='Gravity Information',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('color_min'),
                FieldPanel('color_max'),
            ],
            heading='Color',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('ibu_min'),
                FieldPanel('ibu_max'),
            ],
            heading='IBUs',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                FieldPanel('carbonation_min'),
                FieldPanel('carbonation_max'),
            ],
            heading='Carbonation',
            classname='collapsible collapsed',
        ),
        FieldPanel('notes'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('name', partial_match=True),
        index.SearchField('style_guide', partial_match=True),
        index.SearchField('notes', partial_match=True),
        index.SearchField('category', partial_match=True),
        index.FilterField('style_guide'),
        index.FilterField('color_min'),
        index.FilterField('color_max'),
        index.FilterField('original_gravity_min'),
        index.FilterField('original_gravity_max'),
        index.FilterField('final_gravity_min'),
        index.FilterField('final_gravity_max'),
        index.FilterField('abv_min'),
        index.FilterField('abv_max'),
        index.FilterField('beverage_type'),
        index.FilterField('bjcp_category'),
    ]

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
        ]

    def __str__(self):
        return self.name

    def bjcp_category(self):
        if self.category_number and self.style_letter:
            return f'{self.category_number}{self.style_letter}'
        return ''


class RecipePage(IdAndSlugUrlMixin, Page):
    """
    Page for a beer recipe

    Most of the details come from http://www.beerxml.com/beerxml.htm
    """

    # Tempted to move much of this to a snippet and then the page could just include the snippet.

    template = 'on_tap/recipe_detail.html'

    RECIPE_TYPE_CHOICES = (
        (RecipeType.ALL_GRAIN, 'All Grain'),
        (RecipeType.EXTRACT, 'Extract'),
        (RecipeType.PARTIAL_MASH, 'Partial Mash'),
    )

    VOLUME_UNIT_CHOICES = (
        (VolumeUnit.FLUID_OZ.value, 'Fluid Oz.'),
        (VolumeUnit.LITER.value, 'Liters'),
        (VolumeUnit.GALLON.value, 'Gallons'),
        (VolumeUnit.QUART.value, 'Quarts'),
    )

    tags = ClusterTaggableManager(through=RecipePageTag, blank=True)

    short_description = models.TextField(
        blank=True,
        default='',
        help_text='A one or two sentence description of the recipe.',
    )
    # extract, partial mash, or all grain
    recipe_type = models.CharField(
        max_length=25,
        choices=RECIPE_TYPE_CHOICES,
        blank=False,
        default=RecipeType.ALL_GRAIN,
    )

    # FK to a StylePage or snippet
    # style = models.CharField(max_length=50, blank=False)
    # or use a snippet rather than Page for style?
    # or just enter the text and match up to the page by text in code?
    style = models.ForeignKey(
        'on_tap.BeverageStyle',
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name='recipe_pages',
    )
    brewer = models.CharField(max_length=250, blank=True, default='')  # or fk to a user?
    assistant_brewer = models.CharField(max_length=250, blank=True, default='')

    volume_units = models.CharField(max_length=10, choices=VOLUME_UNIT_CHOICES, blank=False)
    batch_size = models.DecimalField(
        blank=False,
        null=False,
        default=Decimal(0.0),
        max_digits=5,
        decimal_places=2,
        # into fermenter
        help_text='Target size of finished batch in liters.',
    )
    boil_size = models.DecimalField(
        blank=False,
        null=False,
        default=Decimal(0.0),
        max_digits=5,
        decimal_places=2,
        help_text='Starting size for the main boil of the wort in liters.',
    )
    boil_time = models.IntegerField(blank=False, null=False, help_text='Total time to boil the wort in minutes.')
    efficiency = models.SmallIntegerField(
        blank=True,
        null=True,
        default=None,
        help_text='Percent brewhouse efficiency to be used for estimating the starting gravity of the beer. Required for Partial Mash and All Grain recipes.',
    )

    boil_gravity = models.DecimalField(default=None, blank=True, max_digits=4, decimal_places=3, null=True)
    original_gravity = models.DecimalField(default=Decimal(0.0), blank=False, max_digits=4, decimal_places=3)
    final_gravity = models.DecimalField(default=Decimal(0.0), blank=False, max_digits=4, decimal_places=3)
    # I could calculate IBUs but it requires keeping large tables of standard data to do correctly, so
    # for now I will let other software sort that out for me and just enter it here.
    # correction factor is on page 79 of Designing Great Beers book
    # and on http://howtobrew.com/book/section-1/hops/hop-bittering-calculations
    ibus_tinseth = models.DecimalField(default=Decimal(0), max_digits=5, decimal_places=2)

    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )

    # Mash Info Blocks

    # This will come before the recipe, keep it short
    introduction = StreamField(
        STANDARD_STREAMFIELD_FIELDS,
        blank=True,
        null=True,
        default=None,
        help_text='This will be displayed before the recipe information.',
    )

    # This will come after the recipe
    conclusion = StreamField(
        STANDARD_STREAMFIELD_FIELDS,
        blank=True,
        null=True,
        default=None,
        help_text='This will be displayed after the recipe information.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_panels = Page.content_panels + [
        FieldPanel('short_description'),
        FieldPanel('style'),
        FieldPanel('recipe_type'),
        FieldPanel('brewer'),
        FieldPanel('assistant_brewer'),
        MultiFieldPanel(
            [
                FieldPanel('volume_units'),
                FieldPanel('batch_size'),
                FieldPanel('boil_size'),
                FieldPanel('boil_time'),
                FieldPanel('efficiency'),
                FieldPanel('boil_gravity'),
                FieldPanel('original_gravity'),
                FieldPanel('final_gravity'),
                FieldPanel('ibus_tinseth'),
            ],
            heading='Recipe Profile',
            classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'fermentables',
                    label="Fermentables",
                    classname='collapsible collapsed',
                )
            ],
            classname='collapsible collapsed',
            heading='Fermentables',
        ),
        MultiFieldPanel(
            [
                InlinePanel('hops', label="Hops"),
            ],
            classname='collapsible collapsed',
            heading='Hops',
        ),
        MultiFieldPanel(
            [
                InlinePanel(
                    'yeasts',
                    label="Yeast",
                    classname='collapsible collapsed',
                ),
            ],
            classname='collapsible collapsed',
            heading='Yeast',
        ),
        MultiFieldPanel(
            [
                InlinePanel('miscellaneous_ingredients', label="Miscellaneous Ingredients"),
            ],
            classname='collapsible collapsed',
            heading='Miscellaneous Ingredients',
        ),
        FieldPanel('notes'),
        FieldPanel('introduction'),
        FieldPanel('conclusion'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('notes', partial=True),
        index.SearchField('introduction', partial=True),
        index.SearchField('conclusion', partial=True),
        index.SearchField('brewer', partial=True),
        index.SearchField('style'),
        index.RelatedFields('hops', [index.SearchField('name', partial_match=True)]),
        index.RelatedFields('yeasts', [index.SearchField('name', partial_match=True)]),
        index.RelatedFields('fermentables', [index.SearchField('name', partial_match=True)]),
        index.RelatedFields(
            'style',
            (index.SearchField('name', partial_match=True), index.FilterField('name')),
        ),
        index.FilterField('recipe_type'),
        index.FilterField("tags"),
    ]

    subpage_types: list[str] = []
    parent_page_types = [
        'on_tap.RecipeIndexPage',
    ]

    class Meta:
        indexes = [
            models.Index(fields=['recipe_type']),
        ]

    def __str__(self) -> str:
        return self.title

    def get_context(self, request):
        context = super().get_context(request)
        scale_volume = request.GET.get('scale_volume', None)
        scale_unit = request.GET.get('scale_unit', None)
        if scale_volume and scale_unit:
            self.scale_to_volume(Decimal(scale_volume), VolumeUnit(scale_unit))
        return context

    def batch_volume_in_gallons(self) -> Decimal:
        """
        Converts the batch volume to gallons for use in SRM estimation using Morey's equation
        """
        return convert_volume_to_gallons(volume=self.batch_size, unit=VolumeUnit(self.volume_units))

    def calculate_color_srm(self) -> int:
        """
        Returns the estimated color in SRM using Morey's equation of SRM = 1.4922 * (MCU ^ 0.6859).
        """
        # TODO: maybe just store this like I am with everything else, grabbing the value from other software.
        # It was fun to learn and is here now, though.
        total_mcu = Decimal('0')

        for fermentable in self.fermentables.all():
            total_mcu += fermentable.calculate_mcu(self.batch_volume_in_gallons())

        srm = Decimal('1.4922') * (total_mcu ** Decimal('0.6859'))
        return int(srm.quantize(Decimal('1')))

    def calculate_grain_pounds(self) -> Decimal:
        """
        Returns the total weight of grains in pounds
        """
        # TODO: not sure where to put this on UI yet.
        weight = Decimal('0')
        for fermentable in self.fermentables.all():
            weight += fermentable.weight_in_pounds()
        return weight

    def scale_to_volume(self, target_volume: Decimal, unit: VolumeUnit) -> None:
        target_volume_gallons = convert_volume_to_gallons(volume=target_volume, unit=unit)
        scale_factor = target_volume_gallons / self.batch_volume_in_gallons()
        volume_difference = target_volume_gallons - self.batch_volume_in_gallons()

        self.batch_size = target_volume
        self.boil_size = self.boil_size + volume_difference  # TODO: check this
        # TODO: set specified volume units
        self.volume_units = unit.value  # TODO: need to make this TextChoices

        # setting these like this keeps the modified values from the cached queryset
        # rather than a new query the next time self.fermentables.all() (or hops, etc)
        # gets called to iterate later.
        # relying on these having ScalableAmountMixin on them to allow this scaled value to be accessed as `amount`
        # I'm sure I'm doing something unspeakable with that mixin + this here and it's a lot of magic, but it serves my current purpose nicely
        # model_cluster.FakeQuerySet mucks with this stuff, so need to call `get_live_queryset()` first, otherwise this method works once
        # but not on any further calls
        self.fermentables: create_deferring_foreign_related_manager.DeferringRelatedManager = (
            self.fermentables.get_live_queryset().annotate(scaled_amount=F('amount') * scale_factor).all()
        )
        self.hops: create_deferring_foreign_related_manager.DeferringRelatedManager = (
            self.hops.get_live_queryset().all().annotate(scaled_amount=F('amount') * scale_factor)
        )

        self.miscellaneous_ingredients: create_deferring_foreign_related_manager.DeferringRelatedManager = (
            self.miscellaneous_ingredients.get_live_queryset().all().annotate(scaled_amount=F('amount') * scale_factor)
        )
        self.yeasts: create_deferring_foreign_related_manager.DeferringRelatedManager = (
            self.yeasts.get_live_queryset().all().annotate(scaled_amount=F('amount') * scale_factor)
        )

    def get_scaled_recipe(self, target_volume: Decimal, unit: VolumeUnit) -> 'RecipePage':
        """
        Returns a copy of self with volumes scaled to the target volume and units and all ingredient querysets annotated and set up
        for their amounts scaled accordingly
        """
        scaled_recipe = copy.copy(self)
        scaled_recipe.scale_to_volume(target_volume, unit)
        return scaled_recipe


class BatchStatus:
    """
    States a brew batch could be in
    """

    PLANNED = 'planned'
    BREWING = 'brewing'  # why? It's only in this state for a few hours.
    FERMENTING = 'fermenting'
    COMPLETE = 'complete'

    IN_PROGRESS_STATUSES = [PLANNED, BREWING, FERMENTING]


class BatchLogPageTag(TaggedItemBase):
    content_object = ParentalKey("on_tap.batchLogPage", on_delete=models.CASCADE, related_name="tagged_items")


class BatchLogPage(IdAndSlugUrlMixin, Page):
    """
    A homebrew batch intended for use within Wagtail

    TODO: what if I brew one batch, but split it across 2 fermenters with differences at that point?
    TODO: On save, if setting on tap date for first time and status is FERMENTING then change to COMPLETE automatically?
    """

    VOLUME_UNIT_CHOICES = (
        (VolumeUnit.FLUID_OZ.value, 'Fluid Oz.'),
        (VolumeUnit.LITER.value, 'Liters'),
        (VolumeUnit.GALLON.value, 'Gallons'),
        (VolumeUnit.QUART.value, 'Quarts'),
    )

    template = 'on_tap/batch_log.html'
    id_and_slug_url_name = 'on_tap_batch_log_by_id_and_slug'

    tags = ClusterTaggableManager(through=BatchLogPageTag, blank=True)

    recipe_page = models.ForeignKey(
        'on_tap.RecipePage',
        on_delete=models.PROTECT,
        related_name='batch_log_pages',
        blank=False,
        null=False,
    )
    status = models.CharField(
        max_length=25,
        blank=False,
        choices=(
            (BatchStatus.PLANNED, 'Planned'),
            (BatchStatus.BREWING, 'Brewing'),
            (BatchStatus.FERMENTING, 'Fermenting'),
            (BatchStatus.COMPLETE, 'Complete'),
        ),
        default=BatchStatus.PLANNED,
    )
    brewed_date = models.DateField(blank=True, null=True, default=None)
    packaged_date = models.DateField(blank=True, null=True, default=None)
    on_tap_date = models.DateField(blank=True, null=True, default=None)
    off_tap_date = models.DateField(blank=True, null=True, default=None)
    original_gravity = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True, default=None)
    final_gravity = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True, default=None)
    volume_units = models.CharField(
        max_length=10, choices=VOLUME_UNIT_CHOICES, blank=False, default=VolumeUnit.GALLON.value
    )
    post_boil_volume = models.DecimalField(
        blank=True,
        null=True,
        default=None,
        max_digits=5,
        decimal_places=2,
        help_text='Volume of finished batch prior to transfer to fermenter.',
    )
    volume_in_fermenter = models.DecimalField(
        blank=True,
        null=True,
        default=None,
        max_digits=5,
        decimal_places=2,
        help_text='Volume of finished batch in the fermenter.',
    )
    target_post_boil_volume = models.DecimalField(
        blank=True,
        null=True,
        default=None,
        max_digits=5,
        decimal_places=2,
        help_text='Expected volume of finished batch prior to transfer to fermenter. Defaults to the target volume of the selected recipe if not specified.',
    )

    body = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None, use_json_field=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    base_form_class = BatchLogPageForm
    content_panels = Page.content_panels + [
        FieldPanel('recipe_page'),
        FieldPanel('status'),
        FieldPanel('brewed_date'),
        FieldPanel('packaged_date'),
        FieldPanel('on_tap_date'),
        FieldPanel('off_tap_date'),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('original_gravity'),
                        FieldPanel('final_gravity'),
                    ]
                ),
            ],
            heading='Gravity Information',
        ),
        MultiFieldPanel(
            [
                FieldPanel('volume_units'),
                FieldPanel('target_post_boil_volume'),
                FieldPanel('post_boil_volume'),
                FieldPanel('volume_in_fermenter'),
            ]
        ),
        FieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('recipe_page'),
        index.SearchField('body', partial_match=True),
        index.RelatedFields(
            'recipe_page',
            RecipePage.search_fields,
        ),
        index.FilterField("tags"),
        index.FilterField('status'),
        index.FilterField('brewed_date'),
        index.FilterField('packaged_date'),
        index.FilterField('on_tap_date'),
        index.FilterField('off_tap_date'),
        index.FilterField('original_gravity'),
        index.FilterField('final_gravity'),
        index.FilterField('volume_in_fermenter'),
        index.FilterField('target_post_boil_volume'),
    ]

    # log multiple gravity checks?
    subpage_types: list[str] = []
    parent_page_types = [
        'on_tap.BatchLogIndexPage',
    ]

    class Meta:
        indexes = [
            models.Index(fields=['on_tap_date']),
            models.Index(fields=['off_tap_date']),
            models.Index(fields=['brewed_date']),
            models.Index(fields=['status']),
            models.Index(fields=['status', 'brewed_date', 'on_tap_date', 'off_tap_date']),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def uses_scaled_recipe(self) -> bool:
        # might replace this with a BooleanField
        return bool(
            self.target_post_boil_volume
            and (
                self.target_post_boil_volume != self.recipe_page.batch_size
                or self.volume_units != self.recipe_page.volume_units
            )
        )

    @property
    def recipe_url(self) -> str:
        url = self.recipe_page.id_and_slug_url
        if self.uses_scaled_recipe:
            query_params = urlencode({'scale_volume': self.target_post_boil_volume, 'scale_unit': self.volume_units})
            url = f'{url}?{query_params}'
        return mark_safe(url)

    def recipe_scaled_to_target_volume(self) -> RecipePage:
        """
        Returns a new RecipePage matching self.recipe_page which has been scaled to the batches target volume.
        """
        if self.uses_scaled_recipe:
            assert isinstance(self.target_post_boil_volume, Decimal)
            return self.recipe_page.get_scaled_recipe(self.target_post_boil_volume, VolumeUnit(self.volume_units))
        return self.recipe_page

    def get_abv(self) -> Decimal:
        """
        Returns the calculated ABV from gravity readings using the formula (OG-FG) x 131.25 = ABV
        """
        if self.original_gravity is None or self.final_gravity is None:
            raise ValueError('original_gravity and final_gravity must be Decimal values')

        return (self.original_gravity - self.final_gravity) * Decimal('131.25')

    def fermenter_volume_as_gallons(self) -> Decimal:
        """
        Converts the batch volume to gallons for use in SRM estimation using Morey's equation.

        If self.volume_in_fermenter is not specified then the entire recipe_page.batch_size is assumed.
        """
        # TODO: Raise exception if volume_in_fermenter is None?
        if self.volume_in_fermenter is not None:
            volume_in_fermenter: Decimal = self.volume_in_fermenter
        else:
            volume_in_fermenter = self.recipe_page.batch_size
        return convert_volume_to_gallons(volume=volume_in_fermenter, unit=VolumeUnit(self.volume_units))

    def post_boil_volume_as_gallons(self) -> Decimal:
        """
        Converts the post_boil_volume to gallons.

        If self.post_boil_volume is not specified then the entire recipe_page.batch_size is assumed.
        """
        # TODO: Raise exception if post_boil_volume is None?
        if self.post_boil_volume is not None:
            post_boil_volume: Decimal = self.post_boil_volume
        else:
            post_boil_volume = self.recipe_page.batch_size

        return convert_volume_to_gallons(volume=post_boil_volume, unit=VolumeUnit(self.volume_units))

    def calculate_color_srm(self) -> int:
        """
        Returns the estimated color of this batch in SRM using Morey's equation of SRM = 1.4922 * (MCU ^ 0.6859).

        This accounts for differences in actual volume versus the expected volume of the batch. It is assumed that
        the recipe fermentables were used exactly, so if the recipe is written for 2.5 gallons but the batch was scaled
        to 5 gallons then this will not be accurate.
        """
        # TODO: maybe just store this like I am with everything else, grabbing the value from other software.
        # It was fun to learn and is here now, though.
        # TODO: I have this method in 2 places - can I de-duplicate it without just having a fairly pointless one line
        # function? Maybe a calculate_color_srm(fermentables: Iterable[RecipeFermentable], volume: Decimal) which
        # takes volume in gallons
        # TODO: Handle an actual batch which has been scaled up or down to a different intended volume
        total_mcu = Decimal('0')
        if self.uses_scaled_recipe:
            # we know self.target_post_boil_volume is a Decimal here because of the checks in self.uses_scaled_recipe
            # but mypy doesn't seem to know that
            assert isinstance(self.target_post_boil_volume, Decimal)
            recipe_page = self.recipe_page.get_scaled_recipe(
                self.target_post_boil_volume, VolumeUnit(self.volume_units)
            )
        else:
            recipe_page = self.recipe_page
        for fermentable in recipe_page.fermentables.all():
            total_mcu += fermentable.calculate_mcu(self.post_boil_volume_as_gallons())

        srm = Decimal('1.4922') * (total_mcu ** Decimal('0.6859'))
        return int(srm.quantize(Decimal('1')))

    def get_actual_or_expected_srm(self) -> int:
        """
        Returns the actual SRM if final post boil volume is known, otherwise returns the expected SRM
        for the recipe.
        """
        if self.post_boil_volume:
            return self.calculate_color_srm()
        return self.recipe_page.calculate_color_srm()

    def get_context(self, request: HttpRequest) -> dict[str, Any]:
        context = super().get_context(request)
        context['calculated_srm'] = self.get_actual_or_expected_srm()
        if self.target_post_boil_volume:
            context['recipe_page'] = self.recipe_page.get_scaled_recipe(
                self.target_post_boil_volume, VolumeUnit(self.volume_units)
            )
        else:
            context['recipe_page'] = self.recipe_page
        return context


class OnTapPage(Page):
    """
    The main On Tap index
    """

    # TODO: wondering about having per use OnTapPage and an index of OnTapPages - I do not need that currently
    # but seems like a generally interesting idea. Should I make this limit to 1 or 1 per parent?
    # For now, as I am the only user, I will keep this simple.

    template = 'on_tap/on_tap.html'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    subpage_types = [
        'on_tap.RecipeIndexPage',
        'on_tap.BatchLogIndexPage',
    ]

    # or reverse this and use parent_page_types on these other pages?
    # @classmethod
    # def can_create_at(cls, parent):
    #     # You can only create one of these!
    #     return super().can_create_at(parent) \
    #         and not cls.objects.exists()  # I really want one per parent, I think
    #         and parent.get_children().type(OnTapPage).count() == 0  # may be more correct... or .exists()

    def children(self: 'OnTapPage') -> 'QuerySet[Page]':
        return self.get_children().specific().live()

    def get_on_tap_batches(self: 'OnTapPage') -> 'QuerySet[BatchLogPage]':
        """
        Returns the currently on tap batches
        """
        currently_on_tap = BatchLogPage.objects.descendant_of(self).live()
        currently_on_tap = (
            currently_on_tap.filter(on_tap_date__lte=timezone.now(), off_tap_date=None, status=BatchStatus.COMPLETE)
            .exclude(on_tap_date=None)
            .order_by('-on_tap_date')
            .select_related('recipe_page')
        )
        return currently_on_tap

    def get_upcoming_batches(self: 'OnTapPage') -> 'QuerySet[BatchLogPage]':
        """
        Returns the batches which are planned and not currently on tap ordered from newest to oldest. These may be
        just planned, fermenting, or packaged and just waiting to go on tap.
        """
        batches = BatchLogPage.objects.descendant_of(self).live()
        batches = (
            batches.filter(on_tap_date=None, off_tap_date=None)
            .order_by(models.F('brewed_date').desc(nulls_last=True), '-last_published_at')
            .select_related('recipe_page')
        )
        return batches

    def get_past_batches(self: 'OnTapPage') -> 'QuerySet[BatchLogPage]':
        """
        Returns previous batches which are no longer on tap.
        """
        batches = BatchLogPage.objects.descendant_of(self).live()
        batches = (
            batches.filter(status=BatchStatus.COMPLETE)
            .exclude(off_tap_date=None)
            .order_by('-brewed_date', '-last_published_at')
            .select_related('recipe_page')
        )
        return batches

    def paginate(
        self: 'OnTapPage', queryset: 'QuerySet[BatchLogPage]', page_number: int = 1
    ) -> tuple[Paginator, PaginatorPage]:
        paginator = Paginator(queryset, 25)
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)

        return (paginator, page)

    def get_context(self: 'OnTapPage', request: HttpRequest) -> dict:

        context = super().get_context(request)
        currently_on_tap = self.get_on_tap_batches()

        # paginate this
        try:
            page_number = int(request.GET.get('page', 1))
        except Exception:
            page_number = 1

        if page_number == 1:
            upcoming_batches: QuerySet[BatchLogPage] | None = self.get_upcoming_batches()
        else:
            upcoming_batches = None
        past_batches = self.get_past_batches()
        paginator, page = self.paginate(past_batches, page_number)
        context.update(
            {
                'currently_on_tap': currently_on_tap,
                'upcoming_batches': upcoming_batches,
                'past_batches': page.object_list,
                # not the page being viewed, but the paginator page. This is a confusing name in the template context.
                # really need to review django pagination and clean up how I do these.
                'page_obj': page,
                'paginator': paginator,
            }
        )

        return context


class RecipeIndexPage(RoutablePageMixin, IdAndSlugUrlIndexMixin, Page):
    """
    Root index for recipes
    """

    template = 'on_tap/recipe_index.html'
    id_and_slug_url_name = 'on_tap_recipe_by_id_and_slug'
    id_and_slug_url_class = 'bash_shell_net.on_tap.models.RecipePage'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    subpage_types = ['on_tap.RecipePage']

    def children(self: 'RecipeIndexPage') -> 'QuerySet[RecipePage]':
        return self.get_children().specific().live()

    @route(r'^(?P<id>\d+)/(?P<slug>[-_\w]+)/$', name="on_tap_recipe_by_id_and_slug")
    def recipe_by_id_and_slug(self, request, id, slug, *args, **kwargs) -> HttpResponse:
        """
        Look up RecipePage using the id and slug, using just the id for the actual lookup
        """
        # TODO: Find a cleaner way to do this where I do not have to decorate a method here just to directly call
        # the method on IdAndSlugUrlIndexMixin?
        return self.page_by_id_and_slug(request, id, slug, *args, **kwargs)


class BatchLogIndexPage(RoutablePageMixin, IdAndSlugUrlIndexMixin, Page):
    """
    Root index for batches.

    This really only exists so that I can have /on-tap/recipes/foo urls. Other options feel like I am fighting the
    wagtail framework too much.

    TODO: I may be able to make use of RoutablePageMixin on OnTapPage for this although that may cause problems
    for this new IdAndSlugUrlIndexMixin setup.
    """

    template = 'on_tap/recipe_index.html'
    id_and_slug_url_name = 'on_tap_batch_log_by_id_and_slug'
    id_and_slug_url_class = 'bash_shell_net.on_tap.models.BatchLogPage'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    subpage_types = ['on_tap.BatchLogPage']

    def children(self: 'BatchLogIndexPage') -> 'QuerySet[BatchLogPage]':
        return self.get_children().specific().live()

    @route(r'^(?P<id>\d+)/(?P<slug>[-_\w]+)/$', name="on_tap_batch_log_by_id_and_slug")
    def batch_log_by_id_and_slug(self, request, id, slug, *args, **kwargs) -> HttpResponse:
        """
        Look up batchLogPage using the id and slug, using just the id for the actual lookup
        """
        # TODO: Find a cleaner way to do this where I do not have to decorate a method here just to directly call
        # the method on IdAndSlugUrlIndexMixin?
        return self.page_by_id_and_slug(request, id, slug, *args, **kwargs)
