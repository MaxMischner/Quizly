"""
Tests for quiz creation endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class QuizCreateTests(TestCase):
	"""
	Tests for POST /api/quizzes/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.quizzes_url = '/api/quizzes/'
		self.login_url = reverse('login')

		self.user = CustomUser.objects.create_user(
			username='quizuser',
			email='quizuser@example.com',
			password='SecurePassword123'
		)

		login_response = self.client.post(self.login_url, {
			'username': 'quizuser',
			'password': 'SecurePassword123'
		})

		self.access_token = login_response.data.get('access')

	def test_create_quiz_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.post(self.quizzes_url, {
			'url': 'https://www.youtube.com/watch?v=example'
		})

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_create_quiz_success_with_url(self):
		"""
		Create quiz with a valid YouTube URL.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.post(self.quizzes_url, {
			'url': 'https://www.youtube.com/watch?v=example'
		})

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('id', response.data)
		self.assertIn('title', response.data)
		self.assertIn('description', response.data)
		self.assertIn('created_at', response.data)
		self.assertIn('updated_at', response.data)
		self.assertIn('video_url', response.data)
		self.assertIn('questions', response.data)
		self.assertIsInstance(response.data['questions'], list)

		if response.data['questions']:
			question = response.data['questions'][0]
			self.assertIn('id', question)
			self.assertIn('question_title', question)
			self.assertIn('question_options', question)
			self.assertIn('answer', question)
			self.assertIn('created_at', question)
			self.assertIn('updated_at', question)

	def test_create_quiz_missing_url(self):
		"""
		Missing URL should return 400.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.post(self.quizzes_url, {})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_create_quiz_invalid_url(self):
		"""
		Invalid URL should return 400.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.post(self.quizzes_url, {
			'url': 'not-a-valid-url'
		})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
