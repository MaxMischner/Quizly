"""
Tests for quiz update endpoint.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from quizzes.models import Quiz, Question, Answer


class QuizPartialUpdateTests(TestCase):
	"""
	Tests for PATCH /api/quizzes/{id}/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.login_url = reverse('login')

		self.user = CustomUser.objects.create_user(
			username='patchuser',
			email='patchuser@example.com',
			password='SecurePassword123'
		)
		self.other_user = CustomUser.objects.create_user(
			username='otherpatch',
			email='otherpatch@example.com',
			password='SecurePassword123'
		)

		login_response = self.client.post(self.login_url, {
			'username': 'patchuser',
			'password': 'SecurePassword123'
		})
		self.access_token = login_response.data.get('access')

		self.quiz = Quiz.objects.create(
			user=self.user,
			title='Original Title',
			description='Original Description',
			youtube_url='https://www.youtube.com/watch?v=example'
		)
		self.question = Question.objects.create(
			quiz=self.quiz,
			question_text='Question 1',
			order=1
		)
		Answer.objects.create(
			question=self.question,
			answer_text='Option A',
			order=1,
			is_correct=True
		)
		Answer.objects.create(
			question=self.question,
			answer_text='Option B',
			order=2,
			is_correct=False
		)
		Answer.objects.create(
			question=self.question,
			answer_text='Option C',
			order=3,
			is_correct=False
		)
		Answer.objects.create(
			question=self.question,
			answer_text='Option D',
			order=4,
			is_correct=False
		)

		self.detail_url = f'/api/quizzes/{self.quiz.id}/'

	def test_patch_quiz_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.patch(self.detail_url, {
			'title': 'Partially Updated Title'
		})

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_patch_quiz_success_format(self):
		"""
		Partially update quiz and return full details.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.patch(self.detail_url, {
			'title': 'Partially Updated Title',
			'description': 'Partially Updated Description'
		})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('id', response.data)
		self.assertIn('title', response.data)
		self.assertIn('description', response.data)
		self.assertIn('created_at', response.data)
		self.assertIn('updated_at', response.data)
		self.assertIn('video_url', response.data)
		self.assertIn('questions', response.data)

		if response.data['questions']:
			question = response.data['questions'][0]
			self.assertIn('id', question)
			self.assertIn('question_title', question)
			self.assertIn('question_options', question)
			self.assertIn('answer', question)

	def test_patch_quiz_invalid_data(self):
		"""
		Invalid payload should return 400.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

		response = self.client.patch(self.detail_url, {
			'title': ''
		})

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_patch_quiz_not_found(self):
		"""
		Missing quiz should return 404.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		missing_url = '/api/quizzes/999999/'

		response = self.client.patch(missing_url, {
			'title': 'Partially Updated Title'
		})

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_patch_quiz_forbidden_for_other_user(self):
		"""
		Access to another user's quiz should be forbidden.
		"""
		other_quiz = Quiz.objects.create(
			user=self.other_user,
			title='Other Quiz',
			description='Other Description',
			youtube_url='https://www.youtube.com/watch?v=other'
		)
		other_url = f'/api/quizzes/{other_quiz.id}/'

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.patch(other_url, {
			'title': 'Partially Updated Title'
		})

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
