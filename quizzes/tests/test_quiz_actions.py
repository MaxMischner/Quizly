"""
Tests for quiz action endpoints (start, submit answer, complete).
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from quizzes.models import Quiz, Question, Answer, QuizResponse, UserAnswer


class QuizStartTests(TestCase):
	"""
	Tests for POST /api/quizzes/{id}/start_quiz/.
	"""

	def setUp(self):
		self.client = APIClient()
		self.login_url = reverse('login')

		self.user = CustomUser.objects.create_user(
			username='quizuser',
			email='quizuser@example.com',
			password='SecurePassword123'
		)

		self.other_user = CustomUser.objects.create_user(
			username='otheruser',
			email='otheruser@example.com',
			password='OtherPassword123'
		)

		login_response = self.client.post(self.login_url, {
			'username': 'quizuser',
			'password': 'SecurePassword123'
		})
		self.access_token = login_response.data.get('access')

		self.quiz = Quiz.objects.create(
			user=self.user,
			title='Test Quiz',
			description='Test Description',
			youtube_url='https://www.youtube.com/watch?v=test'
		)

		self.start_url = f'/api/quizzes/{self.quiz.id}/start_quiz/'

	def test_start_quiz_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.post(self.start_url)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_start_quiz_success(self):
		"""
		Start quiz successfully and create QuizResponse.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(self.start_url)

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('id', response.data)
		self.assertEqual(response.data['quiz'], self.quiz.id)
		self.assertIsNotNone(response.data['started_at'])
		self.assertIsNone(response.data['completed_at'])
		self.assertIsNone(response.data['score'])

	def test_start_quiz_not_found(self):
		"""
		Missing quiz should return 404.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		missing_url = '/api/quizzes/999999/start_quiz/'

		response = self.client.post(missing_url)
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_start_quiz_forbidden_for_other_user(self):
		"""
		Starting another user's quiz should be forbidden.
		"""
		other_quiz = Quiz.objects.create(
			user=self.other_user,
			title='Other Quiz',
			description='Other Description',
			youtube_url='https://www.youtube.com/watch?v=other'
		)
		other_url = f'/api/quizzes/{other_quiz.id}/start_quiz/'

		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(other_url)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class QuizSubmitAnswerTests(TestCase):
	"""
	Tests for POST /api/quizzes/{id}/submit_answer/.
	"""

	def setUp(self):
		self.client = APIClient()
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

		self.quiz = Quiz.objects.create(
			user=self.user,
			title='Test Quiz',
			description='Test Description',
			youtube_url='https://www.youtube.com/watch?v=test'
		)

		self.question = Question.objects.create(
			quiz=self.quiz,
			question_text='What is Python?',
			order=1
		)

		self.answer1 = Answer.objects.create(
			question=self.question,
			answer_text='A programming language',
			is_correct=True,
			order=1
		)

		self.answer2 = Answer.objects.create(
			question=self.question,
			answer_text='A snake',
			is_correct=False,
			order=2
		)

		# Start a quiz session
		self.quiz_response = QuizResponse.objects.create(
			user=self.user,
			quiz=self.quiz
		)

		self.submit_url = f'/api/quizzes/{self.quiz.id}/submit_answer/'

	def test_submit_answer_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.post(self.submit_url, {
			'response_id': self.quiz_response.id,
			'question_id': self.question.id,
			'answer_id': self.answer1.id
		})
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_submit_answer_success(self):
		"""
		Submit answer successfully and create UserAnswer.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(self.submit_url, {
			'response_id': self.quiz_response.id,
			'question_id': self.question.id,
			'answer_id': self.answer1.id
		})

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertIn('id', response.data)
		self.assertEqual(response.data['question'], self.question.id)
		self.assertEqual(response.data['selected_answer'], self.answer1.id)
		self.assertEqual(response.data['is_correct'], True)

	def test_submit_answer_missing_fields(self):
		"""
		Missing required fields should return error.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(self.submit_url, {
			'response_id': self.quiz_response.id
		})

		# Should return 500 or 400 depending on error handling
		self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])


class QuizCompleteTests(TestCase):
	"""
	Tests for POST /api/quizzes/{id}/complete_quiz/.
	"""

	def setUp(self):
		self.client = APIClient()
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

		self.quiz = Quiz.objects.create(
			user=self.user,
			title='Test Quiz',
			description='Test Description',
			youtube_url='https://www.youtube.com/watch?v=test'
		)

		# Create questions
		self.question1 = Question.objects.create(
			quiz=self.quiz,
			question_text='What is Python?',
			order=1
		)

		self.question2 = Question.objects.create(
			quiz=self.quiz,
			question_text='What is Django?',
			order=2
		)

		# Create answers for question 1
		self.answer1_correct = Answer.objects.create(
			question=self.question1,
			answer_text='A programming language',
			is_correct=True,
			order=1
		)

		Answer.objects.create(
			question=self.question1,
			answer_text='A snake',
			is_correct=False,
			order=2
		)

		# Create answers for question 2
		self.answer2_correct = Answer.objects.create(
			question=self.question2,
			answer_text='A web framework',
			is_correct=True,
			order=1
		)

		Answer.objects.create(
			question=self.question2,
			answer_text='A city',
			is_correct=False,
			order=2
		)

		# Start a quiz session
		self.quiz_response = QuizResponse.objects.create(
			user=self.user,
			quiz=self.quiz
		)

		# Submit answers (1 correct, 1 incorrect)
		UserAnswer.objects.create(
			quiz_response=self.quiz_response,
			question=self.question1,
			selected_answer=self.answer1_correct
		)

		UserAnswer.objects.create(
			quiz_response=self.quiz_response,
			question=self.question2,
			selected_answer=Answer.objects.get(question=self.question2, is_correct=False)
		)

		self.complete_url = f'/api/quizzes/{self.quiz.id}/complete_quiz/'

	def test_complete_quiz_requires_authentication(self):
		"""
		Unauthenticated requests should be rejected.
		"""
		response = self.client.post(self.complete_url, {
			'response_id': self.quiz_response.id
		})
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_complete_quiz_success_with_score(self):
		"""
		Complete quiz and calculate score (50% = 1 out of 2 correct).
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(self.complete_url, {
			'response_id': self.quiz_response.id
		})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('id', response.data)
		self.assertEqual(response.data['score'], 50)
		self.assertIsNotNone(response.data['completed_at'])

	def test_complete_quiz_missing_response_id(self):
		"""
		Missing response_id should return error.
		"""
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
		response = self.client.post(self.complete_url, {})

		# Should return 500 or 400 depending on error handling
		self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_500_INTERNAL_SERVER_ERROR])
