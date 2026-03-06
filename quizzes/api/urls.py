"""URL routes for quiz API endpoints."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quizzes.api.views import QuizViewSet

router = DefaultRouter()
router.register(r"", QuizViewSet, basename="quiz")

urlpatterns = [
    path("", include(router.urls)),
]
