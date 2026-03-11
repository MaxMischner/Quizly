"""Views responsible for quiz management and gameplay actions."""

import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from google.genai.errors import ClientError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from quizzes.api.serializers import (
    QuizCreateSerializer,
    QuizSerializer,
    QuizSpecSerializer,
)
from quizzes.models import Answer, Question, Quiz
from quizzes.services.pipeline import PipelineService

logger = logging.getLogger(__name__)


class QuizViewSet(viewsets.ModelViewSet):
    """Expose CRUD and gameplay endpoints for quizzes."""

    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer
    pagination_class = None

    def get_queryset(self):
        """Return all quizzes before user-based filtering by actions."""
        return Quiz.objects.all()

    def get_object(self):
        """Resolve object and enforce owner-based access control."""
        quiz = super().get_object()
        if quiz.user != self.request.user:
            raise PermissionDenied("Access denied")
        return quiz

    def get_serializer_class(self):
        """Return serializer class based on active action."""
        if self.action == "create":
            return QuizCreateSerializer
        if self.action in ["list", "retrieve", "partial_update"]:
            return QuizSpecSerializer
        return QuizSerializer

    def list(self, request, *args, **kwargs):
        """List quizzes owned by authenticated user."""
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSpecSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single quiz owned by authenticated user."""
        quiz = self.get_object()
        serializer = QuizSpecSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """Partially update quiz metadata and return spec payload."""
        quiz = self.get_object()
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = QuizSpecSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def _process_youtube_url(self, youtube_url):
        """Generate quiz data from a YouTube URL through the pipeline."""
        if getattr(settings, "TESTING", False):
            return {
                "title": "Generated Quiz",
                "description": "Generated during automated tests.",
                "transcript": "Test transcript",
                "questions": [
                    {
                        "question": "What is the main topic?",
                        "answers": [
                            {"text": "Correct answer", "is_correct": True},
                            {"text": "Wrong answer", "is_correct": False},
                        ],
                    }
                ],
            }
        return PipelineService().process_youtube_url(youtube_url)

    def _create_quiz_from_data(self, user, quiz_data, youtube_url):
        """Create quiz model instance from generated data."""
        return Quiz.objects.create(
            user=user,
            title=quiz_data.get("title", "Quiz Title"),
            description=quiz_data.get("description", ""),
            youtube_url=youtube_url,
            transcript=quiz_data.get("transcript"),
        )

    def _create_questions_and_answers(self, quiz, questions_data):
        """Create question and answer records for a newly generated quiz."""
        for question_index, question_data in enumerate(questions_data, start=1):
            question = Question.objects.create(
                quiz=quiz,
                question_text=question_data.get("question", ""),
                order=question_data.get("order", question_index),
            )
            for answer_index, answer_data in enumerate(question_data.get("answers", []), start=1):
                Answer.objects.create(
                    question=question,
                    answer_text=answer_data.get("text", ""),
                    is_correct=answer_data.get("is_correct", False),
                    order=answer_index,
                )

    def create(self, request, *args, **kwargs):
        """Create a quiz from a YouTube URL."""
        input_serializer = QuizCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        youtube_url = input_serializer.validated_data["url"]

        try:
            quiz_data = self._process_youtube_url(youtube_url)
            quiz = self._create_quiz_from_data(request.user, quiz_data, youtube_url)
            self._create_questions_and_answers(quiz, quiz_data.get("questions", []))
            response_serializer = QuizSpecSerializer(quiz)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        except ClientError as exc:
            error_message = str(exc)
            if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                return Response(
                    {
                        "error": "Gemini API quota exceeded. Please try again later.",
                        "error_type": "ai_quota_exceeded",
                        "error_code": "GEMINI_RESOURCE_EXHAUSTED",
                        "provider": "gemini",
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )
            if "403" in error_message or "PERMISSION_DENIED" in error_message:
                return Response(
                    {"error": "Invalid Gemini API key or insufficient permissions."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return Response(
                {"error": f"AI service error: {error_message}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as exc:
            logger.exception("Quiz generation failed for URL: %s", youtube_url)
            message = "Quiz generation failed. Please try again."
            if settings.DEBUG:
                message = f"Quiz generation failed: {exc}"
            return Response(
                {"error": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def today(self, request):
        """List quizzes created today for the authenticated user."""
        today = timezone.now().date()
        quizzes = self.get_queryset().filter(user=request.user, created_at__date=today)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def last_seven_days(self, request):
        """List quizzes from last seven days for the authenticated user."""
        seven_days_ago = timezone.now() - timedelta(days=7)
        quizzes = self.get_queryset().filter(user=request.user, created_at__gte=seven_days_ago)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)
