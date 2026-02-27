"""
URL Routing für Quiz-Management.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from quizzes import views

app_name = 'quizzes'

router = DefaultRouter()
router.register(r'', views.QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]
