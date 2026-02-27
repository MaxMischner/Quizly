"""
Views für Quiz-Management und Spielteilnahme.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from quizzes.models import Quiz, Question, Answer, QuizResponse, UserAnswer
from quizzes.serializers import (
    QuizSerializer, QuestionSerializer, QuizDetailSerializer,
    QuizResponseSerializer, UserAnswerSerializer
)


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Quiz Management.
    Erlaubt CRUD-Operationen (Create, Read, Update, Delete).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer
    
    def get_queryset(self):
        """
        Filtere Quizzes für den aktuellen Benutzer.
        """
        return Quiz.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Speichere den Benutzer beim Erstellen eines Quiz.
        """
        serializer.save(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Nutze DetailSerializer bei retrieve (Detailansicht).
        """
        if self.action == 'retrieve':
            return QuizDetailSerializer
        return QuizSerializer
    
    @action(detail=True, methods=['post'])
    def start_quiz(self, request, pk=None):
        """
        Starte ein Quiz und erstelle eine Spielsession.
        POST /api/quizzes/{id}/start_quiz/
        """
        quiz = self.get_object()
        response = QuizResponse.objects.create(
            user=request.user,
            quiz=quiz
        )
        serializer = QuizResponseSerializer(response)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        """
        Speichere eine Benutzerantwort.
        POST /api/quizzes/{id}/submit_answer/
        {
            "response_id": 1,
            "question_id": 1,
            "answer_id": 2
        }
        """
        data = request.data
        quiz_response = QuizResponse.objects.get(id=data.get('response_id'))
        question = Question.objects.get(id=data.get('question_id'))
        answer = Answer.objects.get(id=data.get('answer_id'))
        
        user_answer = UserAnswer.objects.create(
            quiz_response=quiz_response,
            question=question,
            selected_answer=answer
        )
        serializer = UserAnswerSerializer(user_answer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        """
        Beende ein Quiz und berechne den Score.
        POST /api/quizzes/{id}/complete_quiz/
        {"response_id": 1}
        """
        quiz_response = QuizResponse.objects.get(id=request.data.get('response_id'))
        quiz_response.completed_at = timezone.now()
        
        # Berechne Score
        correct_answers = quiz_response.answers.filter(
            selected_answer__is_correct=True
        ).count()
        total_questions = quiz_response.quiz.questions.count()
        score = int((correct_answers / total_questions) * 100)
        
        quiz_response.score = score
        quiz_response.save()
        
        serializer = QuizResponseSerializer(quiz_response)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Hole Quizzes die heute erstellt wurden.
        GET /api/quizzes/today/
        """
        today = timezone.now().date()
        quizzes = self.get_queryset().filter(created_at__date=today)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def last_seven_days(self, request):
        """
        Hole Quizzes der letzten 7 Tage.
        GET /api/quizzes/last_seven_days/
        """
        seven_days_ago = timezone.now() - timedelta(days=7)
        quizzes = self.get_queryset().filter(created_at__gte=seven_days_ago)
        serializer = self.get_serializer(quizzes, many=True)
        return Response(serializer.data)

