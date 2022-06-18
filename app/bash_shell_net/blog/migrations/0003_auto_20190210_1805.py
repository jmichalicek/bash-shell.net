# Generated by Django 2.1.5 on 2019-02-10 18:05

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0041_group_collection_permissions_verbose_name_plural'),
        ('taggit', '0002_auto_20150616_2121'),
        ('blog', '0002_auto_20160907_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.fields.StreamField([('heading', wagtail.blocks.CharBlock(classname='full title')), ('paragraph', wagtail.blocks.RichTextBlock()), ('code', wagtail.blocks.StructBlock([('language', wagtail.blocks.ChoiceBlock(blank=True, choices=[('', 'Auto'), ('bash', 'Bash/Shell'), ('batch', 'Batch'), ('c', 'C'), ('cpp', 'C++'), ('csharp', 'C#'), ('css', 'CSS'), ('docker', 'Dockerfile'), ('elixir', 'Elixir'), ('go', 'Go'), ('htmldjango', 'Django Template'), ('html', 'HTML'), ('javascript', 'JavaScript'), ('json', 'JSON'), ('lisp', 'Lisp'), ('make', 'Makefile'), ('nginx', 'NGiNX Config'), ('perl', 'Perl'), ('php', 'PHP'), ('python', 'Python'), ('jsx', 'React JSX'), ('ruby', 'Ruby'), ('erb', 'Ruby Template/ERB'), ('sass', 'SASS'), ('scss', 'SCSS'), ('sql', 'SQL'), ('terraform', 'Terraform'), ('yaml', 'YAML')], required=False)), ('code', wagtail.blocks.TextBlock(default='', required=False)), ('line_numbers', wagtail.blocks.ChoiceBlock(choices=[('', 'None'), ('table', 'Table'), ('inline', 'Inline')], required=False))])), ('quote', wagtail.blocks.BlockQuoteBlock()), ('other_page', wagtail.blocks.PageChooserBlock()), ('document', wagtail.documents.blocks.DocumentChooserBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('embed', wagtail.embeds.blocks.EmbedBlock()), ('text', wagtail.blocks.TextBlock()), ('raw_html', wagtail.blocks.RawHTMLBlock())], blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogPageIndex',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='BlogPageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='blog.BlogPage')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_blogpagetag_items', to='taggit.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='blogpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='blog.BlogPageTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
