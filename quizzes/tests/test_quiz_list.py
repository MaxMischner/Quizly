"""
Tests for quiz list endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class QuizListTests(TestCase):
	"""
	Tests for GET /api/quizzes/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.quizzes_url = '/api/quizzes/'
		self.login_url = reverse('login')

		self.user = CustomUser.objects.create_user(
			username='listuser',
			email='listuser@example.com',
			password='SecurePassword123'
		)

		login_response = self.client.post(self.login_url, {
			'username': 'listuser',
			'password': 'SecurePassword123'
		})

		self.access_token = login_response.data.get('access')

	def test_list_quizzes_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.get(self.quizzes_url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_list_quizzes_success_format(self):
		"""
		List quizzes for the authenticated user.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.get(self.quizzes_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIsInstance(response.data, list)

		if response.data:
			quiz = response.data[0]
			self.assertIn('id', quiz)
			self.assertIn('title', quiz)
			self.assertIn('description', quiz)
			self.assertIn('created_at', quiz)
			self.assertIn('updated_at', quiz)
			self.assertIn('video_url', quiz)
			self.assertIn('questions', quiz)
			self.assertIsInstance(quiz['questions'], list)

			if quiz['questions']:
				question = quiz['questions'][0]
				self.assertIn('id', question)
				self.assertIn('question_title', question)
				self.assertIn('question_options', question)
				self.assertIn('answer', question)

	def test_list_quizzes_empty_list(self):
		"""
		When user has no quizzes, response should be an empty list.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.get(self.quizzes_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, [])
