from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.test.client import Client

from models import *

class HostingServiceTests(TestCase):
    """Test the HostingService model"""

    def setUp(self):
        self.hosting_service = HostingService.objects.create(name='Test Code Host')

    def tearDown(self):
        self.hosting_service.delete()

    def test_unicode(self):
        """Test the __unicode__() method ouptut"""

        self.assertEqual(self.hosting_service.name, self.hosting_service.__unicode__())

class LanguageTests(TestCase):
    """Test the Language model"""

    def setUp(self):
        self.language = Language.objects.create(name='Python')

    def tearDown(self):
        self.language.delete()

    def test_unicode(self):
        self.assertEqual(self.language.name, self.language.__unicode__())

    def test_name_unique_constraint(self):
        new_language = Language()
        new_language.name = self.language.name
        self.assertRaises(ValidationError, new_language.validate_unique)

class ProjectTests(TestCase):
    """Test the Project model"""

    def setUp(self):
        self.project = Project.objects.create(name='Test Project')

    def tearDown(self):
        self.project.delete()

    def test_unicode(self):
        self.assertEqual(self.project.name, self.project.__unicode__())

    def test_get_absolute_url(self):
        self.assertEqual(self.project.get_absolute_url(), reverse('bsproject_project', args=[self.project.name]))

    def test_save(self):
        """Test the overridden save() method"""
        self.project.description_markdown = '''**test**'''
        self.project.save()
        self.assertEqual(self.project.description, '''<p><strong>test</strong></p>''')


class FullProjectListViewTests(TestCase):
    """Tests the full_project_list view"""

    def setUp(self):
        self.project = Project.objects.create(name='Test Project')
        self.client = Client()

    def tearDown(self):
        self.project.delete()

    def test_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('bsproject_full_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('projects' in response.context)

        projects = response.context['projects']
        self.assertTrue(self.project in projects)

class ProjectViewTest(TestCase):
    """Tests the project() view"""

    def setUp(self):
        self.project = Project.objects.create(name='Test Project')
        pnews = ProjectNews(published=True, project=self.project,
                            text_markdown='fake news!')
        pnews.full_clean()
        pnews.save()

        self.client = Client()

    def tearDown(self):
        self.project.delete()

    def test_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('bsproject_project', args=[self.project.name]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('project' in response.context)
        self.assertEqual(self.project, response.context['project'])
        self.assertTrue('project_news' in response.context)
        self.assertEqual(response.context['project_news'].count(), 1)

class ProjectNewsTest(TestCase):
    """Test the ProjectNews model"""

    def setUp(self):
        self.project = Project.objects.create(name='Test Project')

    def test_save_method(self):
        news = ProjectNews()
        news.project = self.project
        news.text_markdown = '**test**'
        news.full_clean()
        news.save()
        self.assertEqual(news.text_html, '''<p><strong>test</strong></p>''')

    def test_unicode_method(self):
        news = ProjectNews()
        news.project = self.project
        news.text_markdown = '**test**'
        news.full_clean()
        news.save()
        self.assertEqual(news.__unicode__(), news.text_html)

    def test_published_default(self):
        """Default value of published should be False"""
        news = ProjectNews(project=self.project, text_markdown='test')
        news.full_clean()
        news.save()
        self.assertFalse(news.published)


