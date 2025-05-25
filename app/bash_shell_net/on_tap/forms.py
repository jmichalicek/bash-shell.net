from wagtail.admin.forms import WagtailAdminPageForm


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
