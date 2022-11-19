# Generated by Django 4.1.3 on 2022-11-18 22:52

from django.db import migrations
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('on_tap', '0009_alter_recipepage_conclusion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchlogpage',
            name='body',
            field=wagtail.fields.StreamField(
                [
                    ('heading', wagtail.blocks.CharBlock(form_classname='full title')),
                    (
                        'paragraph',
                        wagtail.blocks.RichTextBlock(
                            features=[
                                'h1',
                                'h2',
                                'h3',
                                'h4',
                                'h5',
                                'h6',
                                'ol',
                                'ul',
                                'bold',
                                'italic',
                                'code',
                                'superscript',
                                'subscript',
                                'strikethrough',
                                'blockquote',
                                'link',
                                'document-link',
                                'image',
                                'embed',
                            ]
                        ),
                    ),
                    (
                        'code',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'language',
                                    wagtail.blocks.ChoiceBlock(
                                        blank=True,
                                        choices=[
                                            ('', 'Auto'),
                                            ('bash', 'Bash/Shell'),
                                            ('batch', 'Batch'),
                                            ('c', 'C'),
                                            ('cpp', 'C++'),
                                            ('csharp', 'C#'),
                                            ('css', 'CSS'),
                                            ('docker', 'Dockerfile'),
                                            ('elixir', 'Elixir'),
                                            ('go', 'Go'),
                                            ('htmldjango', 'Django Template'),
                                            ('html', 'HTML'),
                                            ('javascript', 'JavaScript'),
                                            ('json', 'JSON'),
                                            ('lisp', 'Lisp'),
                                            ('make', 'Makefile'),
                                            ('nginx', 'NGiNX Config'),
                                            ('perl', 'Perl'),
                                            ('php', 'PHP'),
                                            ('python', 'Python'),
                                            ('jsx', 'React JSX'),
                                            ('ruby', 'Ruby'),
                                            ('erb', 'Ruby Template/ERB'),
                                            ('sass', 'SASS'),
                                            ('scss', 'SCSS'),
                                            ('sql', 'SQL'),
                                            ('terraform', 'Terraform'),
                                            ('yaml', 'YAML'),
                                        ],
                                        required=False,
                                    ),
                                ),
                                ('filename', wagtail.blocks.CharBlock(default='', required=False)),
                                ('display_filename', wagtail.blocks.BooleanBlock(default=True, required=False)),
                                ('code', wagtail.blocks.TextBlock(default='', required=False)),
                                (
                                    'line_numbers',
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[('', 'None'), ('table', 'Table'), ('inline', 'Inline')], required=False
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ('quote', wagtail.blocks.BlockQuoteBlock()),
                    ('other_page', wagtail.blocks.PageChooserBlock()),
                    ('document', wagtail.documents.blocks.DocumentChooserBlock()),
                    ('image', wagtail.images.blocks.ImageChooserBlock(template='wagtail_blocks/image.html')),
                    (
                        'image_detail',
                        wagtail.blocks.StructBlock(
                            [
                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                ('caption', wagtail.blocks.CharBlock(label='Caption', max_length=200, required=False)),
                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                            ]
                        ),
                    ),
                    (
                        'image_gallery',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'image_items',
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                                (
                                                    'caption',
                                                    wagtail.blocks.CharBlock(
                                                        label='Caption', max_length=200, required=False
                                                    ),
                                                ),
                                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                                            ]
                                        ),
                                        label='Image',
                                    ),
                                )
                            ]
                        ),
                    ),
                    ('embed', wagtail.embeds.blocks.EmbedBlock()),
                    ('text', wagtail.blocks.TextBlock()),
                    ('raw_html', wagtail.blocks.RawHTMLBlock()),
                ],
                blank=True,
                default=None,
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name='recipepage',
            name='conclusion',
            field=wagtail.fields.StreamField(
                [
                    ('heading', wagtail.blocks.CharBlock(form_classname='full title')),
                    (
                        'paragraph',
                        wagtail.blocks.RichTextBlock(
                            features=[
                                'h1',
                                'h2',
                                'h3',
                                'h4',
                                'h5',
                                'h6',
                                'ol',
                                'ul',
                                'bold',
                                'italic',
                                'code',
                                'superscript',
                                'subscript',
                                'strikethrough',
                                'blockquote',
                                'link',
                                'document-link',
                                'image',
                                'embed',
                            ]
                        ),
                    ),
                    (
                        'code',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'language',
                                    wagtail.blocks.ChoiceBlock(
                                        blank=True,
                                        choices=[
                                            ('', 'Auto'),
                                            ('bash', 'Bash/Shell'),
                                            ('batch', 'Batch'),
                                            ('c', 'C'),
                                            ('cpp', 'C++'),
                                            ('csharp', 'C#'),
                                            ('css', 'CSS'),
                                            ('docker', 'Dockerfile'),
                                            ('elixir', 'Elixir'),
                                            ('go', 'Go'),
                                            ('htmldjango', 'Django Template'),
                                            ('html', 'HTML'),
                                            ('javascript', 'JavaScript'),
                                            ('json', 'JSON'),
                                            ('lisp', 'Lisp'),
                                            ('make', 'Makefile'),
                                            ('nginx', 'NGiNX Config'),
                                            ('perl', 'Perl'),
                                            ('php', 'PHP'),
                                            ('python', 'Python'),
                                            ('jsx', 'React JSX'),
                                            ('ruby', 'Ruby'),
                                            ('erb', 'Ruby Template/ERB'),
                                            ('sass', 'SASS'),
                                            ('scss', 'SCSS'),
                                            ('sql', 'SQL'),
                                            ('terraform', 'Terraform'),
                                            ('yaml', 'YAML'),
                                        ],
                                        required=False,
                                    ),
                                ),
                                ('filename', wagtail.blocks.CharBlock(default='', required=False)),
                                ('display_filename', wagtail.blocks.BooleanBlock(default=True, required=False)),
                                ('code', wagtail.blocks.TextBlock(default='', required=False)),
                                (
                                    'line_numbers',
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[('', 'None'), ('table', 'Table'), ('inline', 'Inline')], required=False
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ('quote', wagtail.blocks.BlockQuoteBlock()),
                    ('other_page', wagtail.blocks.PageChooserBlock()),
                    ('document', wagtail.documents.blocks.DocumentChooserBlock()),
                    ('image', wagtail.images.blocks.ImageChooserBlock(template='wagtail_blocks/image.html')),
                    (
                        'image_detail',
                        wagtail.blocks.StructBlock(
                            [
                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                ('caption', wagtail.blocks.CharBlock(label='Caption', max_length=200, required=False)),
                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                            ]
                        ),
                    ),
                    (
                        'image_gallery',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'image_items',
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                                (
                                                    'caption',
                                                    wagtail.blocks.CharBlock(
                                                        label='Caption', max_length=200, required=False
                                                    ),
                                                ),
                                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                                            ]
                                        ),
                                        label='Image',
                                    ),
                                )
                            ]
                        ),
                    ),
                    ('embed', wagtail.embeds.blocks.EmbedBlock()),
                    ('text', wagtail.blocks.TextBlock()),
                    ('raw_html', wagtail.blocks.RawHTMLBlock()),
                ],
                blank=True,
                default=None,
                help_text='This will be displayed after the recipe information.',
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name='recipepage',
            name='introduction',
            field=wagtail.fields.StreamField(
                [
                    ('heading', wagtail.blocks.CharBlock(form_classname='full title')),
                    (
                        'paragraph',
                        wagtail.blocks.RichTextBlock(
                            features=[
                                'h1',
                                'h2',
                                'h3',
                                'h4',
                                'h5',
                                'h6',
                                'ol',
                                'ul',
                                'bold',
                                'italic',
                                'code',
                                'superscript',
                                'subscript',
                                'strikethrough',
                                'blockquote',
                                'link',
                                'document-link',
                                'image',
                                'embed',
                            ]
                        ),
                    ),
                    (
                        'code',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'language',
                                    wagtail.blocks.ChoiceBlock(
                                        blank=True,
                                        choices=[
                                            ('', 'Auto'),
                                            ('bash', 'Bash/Shell'),
                                            ('batch', 'Batch'),
                                            ('c', 'C'),
                                            ('cpp', 'C++'),
                                            ('csharp', 'C#'),
                                            ('css', 'CSS'),
                                            ('docker', 'Dockerfile'),
                                            ('elixir', 'Elixir'),
                                            ('go', 'Go'),
                                            ('htmldjango', 'Django Template'),
                                            ('html', 'HTML'),
                                            ('javascript', 'JavaScript'),
                                            ('json', 'JSON'),
                                            ('lisp', 'Lisp'),
                                            ('make', 'Makefile'),
                                            ('nginx', 'NGiNX Config'),
                                            ('perl', 'Perl'),
                                            ('php', 'PHP'),
                                            ('python', 'Python'),
                                            ('jsx', 'React JSX'),
                                            ('ruby', 'Ruby'),
                                            ('erb', 'Ruby Template/ERB'),
                                            ('sass', 'SASS'),
                                            ('scss', 'SCSS'),
                                            ('sql', 'SQL'),
                                            ('terraform', 'Terraform'),
                                            ('yaml', 'YAML'),
                                        ],
                                        required=False,
                                    ),
                                ),
                                ('filename', wagtail.blocks.CharBlock(default='', required=False)),
                                ('display_filename', wagtail.blocks.BooleanBlock(default=True, required=False)),
                                ('code', wagtail.blocks.TextBlock(default='', required=False)),
                                (
                                    'line_numbers',
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[('', 'None'), ('table', 'Table'), ('inline', 'Inline')], required=False
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ('quote', wagtail.blocks.BlockQuoteBlock()),
                    ('other_page', wagtail.blocks.PageChooserBlock()),
                    ('document', wagtail.documents.blocks.DocumentChooserBlock()),
                    ('image', wagtail.images.blocks.ImageChooserBlock(template='wagtail_blocks/image.html')),
                    (
                        'image_detail',
                        wagtail.blocks.StructBlock(
                            [
                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                ('caption', wagtail.blocks.CharBlock(label='Caption', max_length=200, required=False)),
                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                            ]
                        ),
                    ),
                    (
                        'image_gallery',
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    'image_items',
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.StructBlock(
                                            [
                                                ('image', wagtail.images.blocks.ImageChooserBlock()),
                                                (
                                                    'caption',
                                                    wagtail.blocks.CharBlock(
                                                        label='Caption', max_length=200, required=False
                                                    ),
                                                ),
                                                ('attribution', wagtail.blocks.CharBlock(required=False)),
                                                ('license_url', wagtail.blocks.URLBlock(required=False)),
                                                ('license_name', wagtail.blocks.CharBlock(required=False)),
                                            ]
                                        ),
                                        label='Image',
                                    ),
                                )
                            ]
                        ),
                    ),
                    ('embed', wagtail.embeds.blocks.EmbedBlock()),
                    ('text', wagtail.blocks.TextBlock()),
                    ('raw_html', wagtail.blocks.RawHTMLBlock()),
                ],
                blank=True,
                default=None,
                help_text='This will be displayed before the recipe information.',
                null=True,
                use_json_field=True,
            ),
        ),
    ]
