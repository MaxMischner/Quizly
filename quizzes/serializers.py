"""Compatibility module that re-exports quiz API serializers."""

from quizzes.api.serializers import (
    AnswerSerializer,
    QuestionSerializer,
    QuizCreateSerializer,
    QuizDetailSerializer,
    QuizSerializer,
    QuizSpecQuestionSerializer,
    QuizSpecSerializer,
)

__all__ = [
    "AnswerSerializer",
    "QuestionSerializer",
    "QuizSerializer",
    "QuizDetailSerializer",
    "QuizCreateSerializer",
    "QuizSpecQuestionSerializer",
    "QuizSpecSerializer",
]
