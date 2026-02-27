"""
Tests for quiz filter endpoints (today, last_seven_days).
"""
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from quizzes.models import Quiz


class QuizTodayTests(TestCase):
	"""
	Tests for GET /api/quizzes/today/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.login_url = reverse('login')
		self.today_url = '/api/quizzes/today/'

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

	def test_today_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.get(self.today_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_today_returns_todays_quizzes(self):
		"""
		Should return only quizzes created today.
		"""
		# Create a quiz today
		today_quiz = Quiz.objects.create(
			user=self.user,
			title='Today Quiz',
			description='Created today',
			youtube_url='https://www.youtube.com/watch?v=today'
		)

		# Create a quiz yesterday
		yesterday_quiz = Quiz.objects.create(
			user=self.user,
			title='Yesterday Quiz',
			description='Created yesterday',
			youtube_url='https://www.youtube.com/watch?v=yesterday'
		)
		yesterday_quiz.created_at = timezone.now() - timedelta(days=1)
		yesterday_quiz.save()

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.today_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['title'], 'Today Quiz')

	def test_today_empty_list(self):
		"""
		Should return empty list if no quizzes today.
		"""
		# Create a quiz yesterday
		yesterday_quiz = Quiz.objects.create(
			user=self.user,
			title='Yesterday Quiz',
			description='Created yesterday',
			youtube_url='https://www.youtube.com/watch?v=yesterday'
		)
		yesterday_quiz.created_at = timezone.now() - timedelta(days=1)
		yesterday_quiz.save()

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.today_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 0)


class QuizLastSevenDaysTests(TestCase):
	"""
	Tests for GET /api/quizzes/last_seven_days/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.login_url = reverse('login')
		self.last_seven_days_url = '/api/quizzes/last_seven_days/'

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

	def test_last_seven_days_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.get(self.last_seven_days_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_last_seven_days_returns_recent_quizzes(self):
		"""
		Should return quizzes from the last 7 days.
		"""
		# Create quiz from 3 days ago
		recent_quiz = Quiz.objects.create(
			user=self.user,
			title='Recent Quiz',
			description='Created 3 days ago',
			youtube_url='https://www.youtube.com/watch?v=recent'
		)
		recent_quiz.created_at = timezone.now() - timedelta(days=3)
		recent_quiz.save()

		# Create quiz from 8 days ago (should not be included)
		old_quiz = Quiz.objects.create(
			user=self.user,
			title='Old Quiz',
			description='Created 8 days ago',
			youtube_url='https://www.youtube.com/watch?v=old'
		)
		old_quiz.created_at = timezone.now() - timedelta(days=8)
		old_quiz.save()

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.last_seven_days_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['title'], 'Recent Quiz')

	def test_last_seven_days_includes_today(self):
		"""
		Should include quizzes created today.
		"""
		# Create quiz today
		today_quiz = Quiz.objects.create(
			user=self.user,
			title='Today Quiz',
			description='Created today',
			youtube_url='https://www.youtube.com/watch?v=today'
		)

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.last_seven_days_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['title'], 'Today Quiz')

	def test_last_seven_days_empty_list(self):
		"""
		Should return empty list if no quizzes in last 7 days.
		"""
		# Create quiz 10 days ago
		old_quiz = Quiz.objects.create(
			user=self.user,
			title='Old Quiz',
			description='Created 10 days ago',
			youtube_url='https://www.youtube.com/watch?v=old'
		)
		old_quiz.created_at = timezone.now() - timedelta(days=10)
		old_quiz.save()

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.get(self.last_seven_days_url)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 0)
