# Generated by Django 3.0.8 on 2020-08-09 18:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("on_tap", "0002_auto_20200801_1345"),
    ]

    operations = [
        migrations.AlterField(
            model_name="batchlogpage",
            name="recipe_page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="batch_log_pages", to="on_tap.RecipePage"
            ),
        ),
    ]
