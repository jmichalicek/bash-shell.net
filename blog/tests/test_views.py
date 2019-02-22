from django.test import TestCase
from django.urls import reverse

from accounts.factories import UserFactory
from .factories import PublishedPostFactory, UnpublishedPostFactory

# TODO: new tests for testing wagtail Page models.

# class PostListViewTests(TestCase):
#     """Test the index view"""
#
#     URL_NAME = 'blog_post_list'
#
#     def setUp(self):
#         # move this to setUpTestData after django upgrade
#         self.published_post = PublishedPostFactory()
#         self.unpublished_post = UnpublishedPostFactory()
#
#     def test_get(self):
#         """Make sure we get a 200 response code"""
#         response = self.client.get(reverse(self.URL_NAME))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.templates[0].name, 'blog/post_list.html')
#         self.assertTrue('post_list' in response.context)
#         self.assertTrue(self.published_post in response.context['post_list'])
#         self.assertFalse(
#             self.unpublished_post in response.context['post_list'])
#
#     def test_empty_page(self):
#         """Verify that a 404 is returned when a page with no results is requested"""
#         response = self.client.get(reverse(self.URL_NAME), {'page': 2})
#         self.assertEqual(response.status_code, 404)


# class PostDetailViewTests(TestCase):
#     """Test the item view"""
#
#     URL_NAME = 'blog_post_detail'
#
#     def setUp(self):
#         # move this to setUpTestData after django upgrade
#         self.post = PublishedPostFactory()
#         self.unpublished_post = UnpublishedPostFactory()
#
#     def test_get(self):
#         """Make sure we get a 200 response code"""
#         response = self.client.get(
#             reverse(self.URL_NAME, args=[self.post.slug]))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.templates[0].name, 'blog/post_detail.html')
#         self.assertTrue('post' in response.context)
#         self.assertTrue('tags' in response.context)
#         self.assertEqual(response.context['post'], self.post)
#
#     def test_get_unpublished(self):
#         response = self.client.get(
#             reverse(self.URL_NAME, args=[self.unpublished_post.slug]))
#         self.assertEqual(response.status_code, 404)
#
#
# class PostPreviewViewTest(TestCase):
#     """
#     Test PostPreviewView
#     """
#
#     URL_NAME = 'blog_post_preview'
#
#     @classmethod
#     def setUpTestData(cls):
#         # move this to setUpTestData after django upgrade
#         cls.post = PublishedPostFactory()
#         cls.unpublished_post = UnpublishedPostFactory()
#         cls.user = UserFactory()
#
#     def test_not_unauthenticated_user_receives_404(self):
#         """
#         Ensure unauthenticated user gets http 404 response
#         """
#         self.clinet.logout()
#         response = self.client.get(
#             reverse(self.URL_NAME, args=[self.unpublished_post.slug]))
#         self.assertEqual(response.status_code, 404)
#
#     def test_get_published_post_while_logged_in_returns_good_response(self):
#         """Make sure we get a 200 response code"""
#         self.client.login(username=self.user.email, password='password')
#         response = self.client.get(
#             reverse(self.URL_NAME, args=[self.post.slug]))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.templates[0].name, 'blog/post_detail.html')
#         self.assertTrue('post' in response.context)
#         self.assertEqual(response.context['post'], self.post)
#
#     def test_get_unpublished_post_while_logged_in_returns_good_response(self):
#         self.client.login(username=self.user.email, password='password')
#         response = self.client.get(
#             reverse(self.URL_NAME, args=[self.unpublished_post.slug]))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.templates[0].name, 'blog/post_detail.html')
#         self.assertTrue('post' in response.context)
#         self.assertEqual(response.context['post'], self.unpublished_post)
