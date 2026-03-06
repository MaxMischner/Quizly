"""Compatibility module that re-exports quiz API views."""

from quizzes.api.views import QuizViewSet

__all__ = ["QuizViewSet"]

