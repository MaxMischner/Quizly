"""Compatibility module that re-exports quiz API serializers."""

from quizzes.api.serializers import (
    AnswerSerializer,
    QuestionSerializer,
    QuizCreateSerializer,
    QuizDetailSerializer,
    QuizResponseSerializer,
    QuizSerializer,
    QuizSpecQuestionSerializer,
    QuizSpecSerializer,
    UserAnswerSerializer,
)

__all__ = [
    "AnswerSerializer",
    "QuestionSerializer",
    "QuizSerializer",
    "QuizDetailSerializer",
    "UserAnswerSerializer",
    "QuizResponseSerializer",
    "QuizCreateSerializer",
    "QuizSpecQuestionSerializer",
    "QuizSpecSerializer",
]
