"""
Tests for quiz delete endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from quizzes.models import Quiz


class QuizDeleteTests(TestCase):
	"""
	Tests for DELETE /api/quizzes/{id}/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.login_url = reverse('login')

		self.user = CustomUser.objects.create_user(
			username='deleteuser',
			email='deleteuser@example.com',
			password='SecurePassword123'
		)
		self.other_user = CustomUser.objects.create_user(
			username='otherdelete',
			email='otherdelete@example.com',
			password='SecurePassword123'
		)

		login_response = self.client.post(self.login_url, {
			'username': 'deleteuser',
			'password': 'SecurePassword123'
		})
		self.access_token = login_response.data.get('access')

		self.quiz = Quiz.objects.create(
			user=self.user,
			title='Delete Quiz',
			description='Delete Description',
			youtube_url='https://www.youtube.com/watch?v=example'
		)
		self.detail_url = f'/api/quizzes/{self.quiz.id}/'

	def test_delete_quiz_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.delete(self.detail_url)

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_delete_quiz_success(self):
		"""
		Delete own quiz successfully.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.delete(self.detail_url)

		self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

	def test_delete_quiz_not_found(self):
		"""
		Missing quiz should return 404.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		missing_url = '/api/quizzes/999999/'

		response = self.client.delete(missing_url)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_quiz_forbidden_for_other_user(self):
		"""
		Access to delete another user's quiz should be forbidden.
		"""
		other_quiz = Quiz.objects.create(
			user=self.other_user,
			title='Other Quiz',
			description='Other Description',
			youtube_url='https://www.youtube.com/watch?v=other'
		)
		other_url = f'/api/quizzes/{other_quiz.id}/'

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.delete(other_url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
