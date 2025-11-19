from django import forms

from wagtail.admin.forms import WagtailAdminPageForm

from bash_shell_net.on_tap.beerxml_parser import BeerXMLParseError, parse_beerxml


class RecipePageForm(WagtailAdminPageForm):
    """
    Custom admin form for RecipePage with BeerXML import functionality.
    """

    beerxml_import = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 10, "placeholder": "Paste BeerXML here to import a recipe..."}),
        label="Import from BeerXML",
        help_text="Paste BeerXML data here to pre-populate the recipe. This will NOT set style information - you'll need to set that manually.",
    )

    def clean(self):
        """Process BeerXML import if provided."""
        cleaned_data = super().clean()
        beerxml_content = cleaned_data.get("beerxml_import")

        if beerxml_content and beerxml_content.strip():
            try:
                recipe_data = parse_beerxml(beerxml_content)

                # Update the cleaned_data with parsed values
                # Only update if the field is empty or has the default value
                for field_name, value in recipe_data.items():
                    if field_name in ["fermentables", "hops", "yeasts", "miscellaneous_ingredients"]:
                        # These will be handled in save()
                        continue

                    # Only override if field is empty or unchanged
                    if field_name in cleaned_data:
                        current_value = cleaned_data.get(field_name)
                        # Update if empty string, None, or default values
                        if not current_value or current_value in ["", 0, "1.000"]:
                            cleaned_data[field_name] = value
                    else:
                        cleaned_data[field_name] = value

                # Store the full recipe data for use in save()
                self._beerxml_recipe_data = recipe_data

            except BeerXMLParseError as e:
                raise forms.ValidationError(f"Error parsing BeerXML: {e}")
            except Exception as e:
                raise forms.ValidationError(f"Unexpected error parsing BeerXML: {e}")

        return cleaned_data

    def save(self, commit=True):
        """Save the form and create related ingredient records if BeerXML was imported."""
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # If we have BeerXML data, create the related ingredients
            if hasattr(self, "_beerxml_recipe_data"):
                recipe_data = self._beerxml_recipe_data
                self._create_fermentables(instance, recipe_data.get("fermentables", []))
                self._create_hops(instance, recipe_data.get("hops", []))
                self._create_yeasts(instance, recipe_data.get("yeasts", []))
                self._create_misc_ingredients(instance, recipe_data.get("miscellaneous_ingredients", []))

        return instance

    def _create_fermentables(self, recipe_page, fermentables_data):
        """Create RecipeFermentable instances from parsed data."""
        from bash_shell_net.on_tap.models import RecipeFermentable

        for idx, ferm_data in enumerate(fermentables_data):
            RecipeFermentable.objects.create(recipe_page=recipe_page, sort_order=idx, **ferm_data)

    def _create_hops(self, recipe_page, hops_data):
        """Create RecipeHop instances from parsed data."""
        from bash_shell_net.on_tap.models import RecipeHop

        for idx, hop_data in enumerate(hops_data):
            RecipeHop.objects.create(recipe_page=recipe_page, sort_order=idx, **hop_data)

    def _create_yeasts(self, recipe_page, yeasts_data):
        """Create RecipeYeast instances from parsed data."""
        from bash_shell_net.on_tap.models import RecipeYeast

        for idx, yeast_data in enumerate(yeasts_data):
            RecipeYeast.objects.create(recipe_page=recipe_page, sort_order=idx, **yeast_data)

    def _create_misc_ingredients(self, recipe_page, misc_data):
        """Create RecipeMiscIngredient instances from parsed data."""
        from bash_shell_net.on_tap.models import RecipeMiscIngredient

        for idx, misc_item_data in enumerate(misc_data):
            RecipeMiscIngredient.objects.create(recipe_page=recipe_page, sort_order=idx, **misc_item_data)


class BatchLogPageForm(WagtailAdminPageForm):
    """
    Custom admin form for BatchLogPage with improved initial data and validation.
    """

    def clean(self):
        cleaned_data = super().clean()

        recipe_page = cleaned_data.get("recipe_page")
        target_post_boil_volume = cleaned_data.get("target_post_boil_volume")

        if recipe_page and not target_post_boil_volume:
            cleaned_data["target_post_boil_volume"] = recipe_page.batch_size
        return cleaned_data
