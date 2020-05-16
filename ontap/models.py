from decimal import Decimal

from django.contrib.postgres.fields import CICharField
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.core.fields import StreamField, RichTextField
from wagtail.core.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail_blocks.fields import STANDARD_STREAMFIELD_FIELDS


class RecipeHop(Orderable, models.Model):
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
        'ontap.RecipePage', on_delete=models.CASCADE, related_name='hops', blank=False, null=False
    )
    name = CICharField(max_length=100, blank=False)
    # A couple extra digits and decimal places to play it safe
    # Could also go FloatField and just be sure to round consistently
    alpha_acid_percent = models.DecimalField(max_digits=6, decimal_places=3, blank=False, null=False)
    amount = models.DecimalField(max_digits=6, decimal_places=2, blank=False, null=False)
    amount_units = models.CharField(max_length=5, choices=(('g', 'Grams'), ('oz', 'Ounces')))
    # use_step maps to BeerXML <USE>
    use_step = models.CharField(choices=USE_STEP_CHOICES, max_length=15, blank=False)
    use_time = models.DurationField(
        blank=False, null=False, help_text='Time in minutes. Specific meaning varies by use type.'
    )
    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )

    # type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    form = models.CharField(max_length=10, choices=FORM_CHOICES)
    beta_acid_percent = models.DecimalField(blank=True, default=None, max_digits=6, decimal_places=3)

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


class RecipeFermentable(Orderable, models.Model):
    """
    A fermentable such as a grain or malt extract used in a recipe

    The term "fermentable" encompasses all fermentable items that contribute substantially to the beer including
    extracts, grains, sugars, honey, fruits.
    """

    UNIT_CHOICES = (
        ('g', 'Grams',),
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
        'ontap.RecipePage', on_delete=models.CASCADE, related_name='fermentables', blank=False, null=False
    )
    amount = models.DecimalField(max_digits=6, decimal_places=3, blank=False, null=False)
    amount_units = models.CharField(max_length=5, blank=False, choices=UNIT_CHOICES,)
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
    type = models.CharField(max_length=25, choices=TYPE_CHOICES, blank=False)
    color = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        blank=True,
        null=True,
        default=None,  # assuming sugars may have no Lovibond or SRM value
        help_text='The color of the item in Lovibond Units (SRM for liquid extracts).',
    )

    panels = [
        FieldPanel('name'),
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


class RecipeYeast(Orderable, models.Model):
    """
    A yeast used in a recipe.

    The term "yeast" encompasses all yeasts, including dry yeast, liquid yeast and yeast starters.

    Like RecipeHop and RecipeFermentable - a good candidate to have an FK back to a base Yeast
    """

    UNIT_CHOICES = (
        ('', '---------'),
        ('Weight', (('g', 'Grams',), ('oz', 'Ounces'),),),
        ('Volume', (('tsp', 'Teaspoons'), ('tbsp', 'Tablespoons'), ('fl_oz', 'Fluid Oz'), ('l', 'Liters'),),),
    )
    recipe_page = ParentalKey(
        'ontap.RecipePage', on_delete=models.CASCADE, related_name='yeasts', blank=False, null=False
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

    class Meta:
        # sort_order is on Orderable
        ordering = ('recipe_page', 'sort_order')

    def amount_is_weight(self) -> bool:
        return amount_units in ['g', 'oz']

    def __str__(self) -> str:
        return self.name

    class RecipeMiscIngredient(Orderable, models.Model):
        """
        The term "misc" encompasses all non-fermentable miscellaneous ingredients that are not hops or yeast and do not
        significantly change the gravity of the beer.  For example: spices, clarifying agents, water treatments, etc…

        Like RecipeHop and RecipeFermentable - a good candidate to have an FK back to a base Yeast
        """

        UNIT_CHOICES = (
            ('Weight', (('g', 'Grams'), ('oz', 'Ounces'), ('kg', 'Kilograms'), ('lb', 'Pounds'),),),
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
            'ontap.RecipePage',
            on_delete=models.CASCADE,
            related_name='miscellaneous_ingredients',
            blank=False,
            null=False,
        )
        amount = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True, default=None)
        amount_units = models.CharField(max_length=5, choices=UNIT_CHOICES, blank=False)
        use_time = models.DurationField(
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

        def __str__(self) -> str:
            return self.name


@register_snippet
class BeverageStyle(models.Model):
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
    beverage_type = models.CharField(max_length=25, blank=True, default='', db_index=True)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('beverage_type'),
        MultiFieldPanel(
            [
                FieldPanel('style_guide'),
                FieldPanel('category'),
                FieldPanel('category_number'),
                FieldPanel('style_number'),
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
            [FieldPanel('color_min'), FieldPanel('color_max'),], heading='Color', classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [FieldPanel('ibu_min'), FieldPanel('ibu_max'),], heading='IBUs', classname='collapsible collapsed',
        ),
        MultiFieldPanel(
            [FieldPanel('carbonation_min'), FieldPanel('carbonation_max'),],
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
        return f'{self.style_number}{self.style_letter}'


class RecipeType:
    """
    The type of beer recipe
    """

    # or just use ints and enum this?
    ALL_GRAIN = 'all_grain'
    EXTRACT = 'extract'
    PARTIAL_MASH = 'partial_mash'


class RecipePage(Page):
    """
    Page for a beer recipe

    Most of the details come from http://www.beerxml.com/beerxml.htm
    """

    template = 'on_tap/recipe.html'
    RECIPE_TYPE_CHOICES = (
        (RecipeType.ALL_GRAIN, 'All Grain'),
        (RecipeType.EXTRACT, 'Extract'),
        (RecipeType.PARTIAL_MASH, 'Partial Mash'),
    )

    # Do I need a separate recipe name and page title?
    name = CICharField(max_length=100, blank=False)
    # extract, partial mash, or all grain
    recipe_type = models.CharField(
        max_length=25, choices=RECIPE_TYPE_CHOICES, blank=False, default=RecipeType.ALL_GRAIN
    )

    # FK to a StylePage or snippet
    # style = models.CharField(max_length=50, blank=False)
    # or use a snippet rather than Page for style?
    # or just enter the text and match up to the page by text in code?
    style = models.ForeignKey(
        'ontap.BeverageStyle', null=True, default=None, on_delete=models.SET_NULL, related_name='recipe_pages',
    )
    brewer = models.CharField(max_length=250, blank=False)
    assistant_brewer = models.CharField(max_length=250, blank=True, default='')

    batch_size = models.DecimalField(
        blank=False,
        null=False,
        default=Decimal(0.0),
        max_digits=5,
        decimal_places=2,
        # Is this into fermenter after boil and trub losses or is this out of the fermenter?
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
    boil_time = models.DurationField(blank=False, null=False, help_text='Total time to boil the wort in minutes.')
    efficiency = models.SmallIntegerField(
        blank=True,
        null=True,
        default=None,
        help_text='Percent brewhouse efficiency to be used for estimating the starting gravity of the beer. Required for Partial Mash and All Grain recipes.',
    )

    notes = RichTextField(
        blank=True,
        default='',
        features=['superscript', 'subscript', 'strikethrough', 'bold', 'italic', 'ul', 'ol', 'link'],
    )

    # Mash Info Blocks

    # This will come before the recipe, keep it short
    introduction = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None)

    # This will come after the recipe
    conclusion = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None)

    content_panels = Page.content_panels + [
        SnippetChooserPanel('style', 'ontap.BeverageStyle'),
        InlinePanel('fermentables', label="Fermentables"),
        InlinePanel('hops', label="Hops"),
        InlinePanel('yeasts', label="Yeasts"),
        InlinePanel('miscellaneous_ingredients', label="Miscellaneous Ingredients"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('name', partial=True, boost=2),  # should this just be Page.title?
        index.SearchField('notes', partial=True),
        index.SearchField('introduction', partial=True),
        index.SearchField('conclusion', partial=True),
        index.SearchField('brewer'),
        index.SearchField('assistant_brewer'),
        index.SearchField('style'),
        index.RelatedFields('hops', index.SearchField('name', partial_match=True)),
        index.RelatedFields('yeast', index.SearchField('name', partial_match=True)),
        index.RelatedFields('fermentables', index.SearchField('name', partial_match=True)),
        index.RelatedFields('style', index.SearchField('name', partial_match=True), index.FilterField('name'),),
        index.FilterField('recipe_type'),
    ]

    class Meta:
        verbose_name = 'Homebrew Recipe Page'
        ordering = ('name',)
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['recipe_type']),
        ]

    def __str__(self):
        return self.name


class BatchLogPage(models.Model):
    """
    A homebrew batch intended for use within Wagtail

    possibly should make a Page for this? Then it can act like a log
    """

    template = 'on_tap/batch_log.html'

    recipe_page = ParentalKey(
        'ontap.RecipePage', on_delete=models.CASCADE, related_name='batch_log_pages', blank=False, null=False
    )

    ontap_page = ParentalKey(
        'ontap.OnTapPage', on_delete=models.CASCADE, related_name='batch_log_pages', blank=False, null=False
    )

    recipe = models.ForeignKey('ontap.RecipePage', blank=True, null=True, default=None, on_delete=models.SET_NULL)
    is_on_tap = models.BooleanField(blank=True, default=False)
    status = models.CharField(
        blank=False,
        choices=(
            ('planned', 'Planned'),
            ('brewing', 'Brewing'),
            ('fermenting', 'Fermenting'),
            ('complete', 'Complete'),
        ),
        default='planned',
    )
    brewed_date = models.DateField(blank=True, null=True, default=None)
    packaged_date = models.DateField(blank=True, null=True, default=None)
    on_tap_date = models.DateField(blank=True, null=True, default=None)
    original_gravity = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True, default=None)
    final_gravity = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True, default=None)
    body = StreamField(STANDARD_STREAMFIELD_FIELDS, blank=True, null=True, default=None)

    search_fields = Page.search_fields + [
        index.SearchField('recipe'),
        index.SearchField('body', partial_match=True),
        index.RelatedFields('recipe_page', RecipePage.search_fields,),
        index.FilterField('is_on_tap'),
        index.FilterField('status'),
        index.FilterField('brewed_date'),
        index.FilterField('packaged_date'),
        index.FilterField('on_tap_date'),
    ]

    # log multiple gravity checks?

    def __str__(self):
        return f'{self.recipe} brewed {self.brewed_date}'

    def get_abv(self) -> Decimal:
        """
        Returns the calculated ABV from gravity readings using the formula (OG-FG) x 131.25 = ABV
        """
        return (self.original_gravity - self.final_gravity) * Decimal('131.25')


class OnTapPage(Page):
    """
    The main On Tap index
    """

    template = 'on_tap/on_tap.html'

    def children(self) -> List[Page]:
        return self.get_children().specific().live()

    def get_context(self, request) -> dict:

        context = super().get_context(request)
        currently_on_tap = BatchLogPage.objects.descendant_of(self).live()
        currently_on_tap = currently_on_tap.filter(is_on_tap=True).order_by('-on_tap_date')

        # paginate this
        batches = BatchLogPage.objects.descendant_of(self).live()
        batches = batches.filter(is_on_tap=False).order_by('brewed_date', 'last_published_at')

        paginator = Paginator(batches, 25)
        page_number = request.GET.get('page')
        try:
            page = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            page = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            page = paginator.page(paginator.num_pages)

        context.update(
            {
                'currently_on_tap': currently_on_tap,
                'batches': page.object_list,
                'page_obj': page,
                'paginator': paginator,
            }
        )
        return context
