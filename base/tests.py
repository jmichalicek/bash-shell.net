from django.test import SimpleTestCase, override_settings
from django.template import Template, Context
import textwrap
from django.conf import settings


class ClickyJsTemplateTagTest(SimpleTestCase):
    def setUp(self):
        self.template = Template(
            """
        {% load clicky_stats %}
        {% clicky_stats_js %}
        """
        )

    @override_settings(CLICKY_SITE_ID='1234')
    def test_clicky_site_id_set(self):
        expected = textwrap.dedent(
            f'''
            <script>var clicky_site_ids = clicky_site_ids || []; clicky_site_ids.push(1234);</script>
            <script async src="//static.getclicky.com/js"></script>
            '''
        ).strip()
        c = Context({})
        rendered = self.template.render(c).strip()
        self.assertEqual(expected, rendered)

    @override_settings(CLICKY_SITE_ID=None)
    def test_clicky_site_id_is_none(self):

        c = Context({})
        rendered = self.template.render(c).strip()
        self.assertEqual('', rendered)

    @override_settings()
    def test_no_clicky_site_id_setting(self):
        del settings.CLICKY_SITE_ID
        c = Context({})
        rendered = self.template.render(c).strip()
        self.assertEqual('', rendered)
