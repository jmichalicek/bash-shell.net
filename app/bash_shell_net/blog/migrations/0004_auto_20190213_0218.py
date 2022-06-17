# Generated by Django 2.1.5 on 2019-02-13 02:18

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20190210_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpage',
            name='body',
            field=wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('code', wagtail.blocks.StructBlock([('language', wagtail.blocks.ChoiceBlock(blank=True, choices=[('', 'Auto'), ('bash', 'Bash/Shell'), ('batch', 'Batch'), ('c', 'C'), ('cpp', 'C++'), ('csharp', 'C#'), ('css', 'CSS'), ('docker', 'Dockerfile'), ('elixir', 'Elixir'), ('go', 'Go'), ('htmldjango', 'Django Template'), ('html', 'HTML'), ('javascript', 'JavaScript'), ('json', 'JSON'), ('lisp', 'Lisp'), ('make', 'Makefile'), ('nginx', 'NGiNX Config'), ('perl', 'Perl'), ('php', 'PHP'), ('python', 'Python'), ('jsx', 'React JSX'), ('ruby', 'Ruby'), ('erb', 'Ruby Template/ERB'), ('sass', 'SASS'), ('scss', 'SCSS'), ('sql', 'SQL'), ('terraform', 'Terraform'), ('yaml', 'YAML')], required=False)), ('filename', wagtail.blocks.CharBlock(default='', required=False)), ('display_filename', wagtail.blocks.BooleanBlock(default=True, required=False)), ('code', wagtail.blocks.TextBlock(default='', required=False)), ('line_numbers', wagtail.blocks.ChoiceBlock(choices=[('', 'None'), ('table', 'Table'), ('inline', 'Inline')], required=False))])), ('quote', wagtail.blocks.BlockQuoteBlock()), ('other_page', wagtail.blocks.PageChooserBlock()), ('document', wagtail.documents.blocks.DocumentChooserBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('text', wagtail.blocks.TextBlock()), ('raw_html', wagtail.blocks.RawHTMLBlock())], blank=True, default=None, null=True),
        ),
    ]
