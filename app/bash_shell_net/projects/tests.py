from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from bash_shell_net.projects.factories import ActiveProjectFactory, ProjectFactory
from bash_shell_net.projects.models import HostingService, Language, Project, ProjectNews


class HostingServiceTests(TestCase):
    """Test the HostingService model"""

    hosting_service: HostingService

    def setUp(self):
        self.hosting_service = HostingService.objects.create(name="Test Code Host")

    def tearDown(self):
        self.hosting_service.delete()

    def test_str(self):
        """Test the __str__() method ouptut"""

        self.assertEqual(self.hosting_service.name, self.hosting_service.__str__())


class LanguageTests(TestCase):
    """Test the Language model"""

    language: Language

    def setUp(self):
        self.language = Language.objects.create(name="Python")

    def tearDown(self):
        self.language.delete()

    def test_str(self):
        self.assertEqual(self.language.name, self.language.__str__())

    def test_name_unique_constraint(self):
        new_language = Language()
        new_language.name = self.language.name
        self.assertRaises(ValidationError, new_language.validate_unique)


class ProjectTests(TestCase):
    """Test the Project model"""

    project: Project

    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = ProjectFactory.create()

    def test_str(self) -> None:
        self.assertEqual(self.project.name, self.project.__str__())

    def test_get_absolute_url(self) -> None:
        self.assertEqual(self.project.get_absolute_url(), reverse("projects_project_detail", args=[self.project.slug]))

    def test_save(self) -> None:
        """
        Test that save sets slug if it is not set
        """
        p = Project(name="new project")
        p.save()
        self.assertEqual("new-project", p.slug)

        # test that it does not reset if we have changed it
        p.slug = "asdf-1234"
        p.save()
        self.assertEqual("asdf-1234", p.slug)


class ProjectListViewTests(TestCase):
    """Tests the full_project_list view"""

    project: Project

    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = ActiveProjectFactory.create()

    def test_view_not_logged_in(self) -> None:
        self.client.logout()
        response = self.client.get(reverse("projects_project_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue("project_list" in response.context)

        projects = response.context["project_list"]
        self.assertTrue(self.project in list(projects))


class ProjectViewTest(TestCase):
    """Tests the project() view"""

    project: Project

    @classmethod
    def setUpTestData(cls):
        cls.project = ActiveProjectFactory.create()
        pnews = ProjectNews(is_published=True, project=cls.project, content="fake news!", title="whee")
        pnews.full_clean()
        pnews.save()

    def test_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("projects_project_detail", args=[self.project.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue("project" in response.context)
        self.assertEqual(self.project, response.context["project"])
        self.assertTrue("project_news" in response.context)
        self.assertEqual(response.context["project_news"].count(), 1)


class ProjectNewsTest(TestCase):
    """Test the ProjectNews model"""

    project: Project

    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = ProjectFactory.create()

    def test_str_method(self) -> None:
        news = ProjectNews(project=self.project)
        news.title = "News Title"
        self.assertEqual(news.__str__(), "News Title")

    def test_published_default(self) -> None:
        """Default value of published should be False"""
        news = ProjectNews(project=self.project, content="test")
        news.save()
        self.assertFalse(news.is_published)
