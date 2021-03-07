import textwrap
import unittest

from django.test import SimpleTestCase, TestCase

from wagtail.core.blocks import BoundBlock
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests, WagtailTestUtils

from . import blocks


class CodeBlockTest(WagtailTestUtils, SimpleTestCase):
    maxDiff = None

    def test_render(self):

        test_matrix = [
            {
                'code': textwrap.dedent(
                    """
                    def foo(*args, **kwargs):
                        print('foobar')
                    """
                ),
                'language': blocks.CodeHighlightLanguage.AUTO,
                'filename': 'foo.py',
                'display_filename': False,
                'line_numbers': blocks.LineNumberStyle.NONE,
                'expected': textwrap.dedent(
                    """
                    <div class="codehilite"><pre><span></span>def foo(*args, **kwargs):
                        print(&#39;foobar&#39;)
                    </pre></div>
                    """
                ),
            },
            {
                'code': textwrap.dedent(
                    """
                    def foo(*args, **kwargs):
                        print('foobar')
                    """
                ),
                'language': blocks.CodeHighlightLanguage.PYTHON,
                'filename': 'foo.py',
                'display_filename': True,
                'line_numbers': blocks.LineNumberStyle.NONE,
                'expected': textwrap.dedent(
                    """
                    <p><code>foo.py:</code></p>
                    <div class="codehilite"><pre><span></span><span class="k">def</span> <span class="nf">foo</span><span class="p">(</span><span class="o">*</span><span class="n">args</span><span class="p">,</span> <span class="o">**</span><span class="n">kwargs</span><span class="p">):</span>
                        <span class="nb">print</span><span class="p">(</span><span class="s1">&#39;foobar&#39;</span><span class="p">)</span>
                    </pre></div>
                    """
                ),
            },
        ]

        block = blocks.CodeBlock()

        for t in test_matrix:
            with self.subTest(language=t['language']):

                render_values = block.get_default()
                render_values.update(
                    {
                        'code': t['code'],
                        'line_numbers': t['line_numbers'],
                        'language': t['language'],
                        'display_filename': t['display_filename'],
                        'filename': t['filename'],
                    }
                )
                self.assertEqual(t['expected'].strip(), block.render(render_values).strip())

    def test_child_blocks(self):
        """
        Tests that the expected keys are in child_blocks.

        This is not entirely necessary, it is more or less covered by test_get_form_context()
        """
        block = blocks.CodeBlock(code="")
        self.assertEqual(
            ['language', 'filename', 'display_filename', 'code', 'line_numbers'], list(block.child_blocks.keys())
        )

    def test_get_form_context(self):
        """
        Test that the form generated for this block has all of the fields which are expected.
        To some extent this test is overkill in that the base StructBlock functionality is already tested
        by wagtail's own tests
        """

        block = blocks.CodeBlock(code="")
        context = block.get_form_context(
            block.to_python(
                {
                    'code': '',
                    'line_numbers': blocks.LineNumberStyle.NONE,
                    'language': blocks.CodeHighlightLanguage.AUTO,
                    'display_filename': True,
                    'filename': 'foo.py',
                }
            ),
        )

        self.assertEqual(5, len(context['children']))
        self.assertTrue(isinstance(context['children']['language'], BoundBlock))
        self.assertTrue(isinstance(context['children']['display_filename'], BoundBlock))
        self.assertTrue(isinstance(context['children']['line_numbers'], BoundBlock))
        self.assertTrue(isinstance(context['children']['filename'], BoundBlock))
        self.assertTrue(isinstance(context['children']['code'], BoundBlock))

        self.assertEqual(context['children']['language'].value, blocks.CodeHighlightLanguage.AUTO)
        self.assertEqual(context['children']['display_filename'].value, True)
        self.assertEqual(context['children']['line_numbers'].value, blocks.LineNumberStyle.NONE)
        self.assertEqual(context['children']['filename'].value, 'foo.py')
        self.assertEqual(context['children']['code'].value, '')
        self.assertEqual(context['block_definition'], block)
