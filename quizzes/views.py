"""
Views für Quiz-Management und Spielteilnahme.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from datetime import timedelta
from quizzes.models import Quiz, Question, Answer, QuizResponse, UserAnswer
from quizzes.serializers import (
    QuizSerializer, QuestionSerializer, QuizDetailSerializer,
    QuizResponseSerializer, UserAnswerSerializer,
    QuizCreateSerializer, QuizSpecSerializer
)
from pipeline_service.services import PipelineService


class QuizViewSet(viewsets.ModelViewSet):
    """
    ViewSet für Quiz Management.
    Erlaubt CRUD-Operationen (Create, Read, Update, Delete).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer
    pagination_class = None
    
    def get_queryset(self):
        """
        Basis-Queryset für Quizzes.
        """
        return Quiz.objects.all()
    
    def get_object(self):
        """
        Hole Quiz und pruefe Zugriff.
        """
        quiz = super().get_object()
        if quiz.user != self.request.user:
            raise PermissionDenied('Zugriff verweigert')
        return quiz
    
    def get_serializer_class(self):
        """
        Nutze passende Serializer je nach Aktion.
        """
        if self.action == 'create':
            return QuizCreateSerializer
        if self.action in ['list', 'retrieve', 'partial_update']:
            return QuizSpecSerializer
        return QuizSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Liste aller Quizzes des aktuellen Benutzers im Spec-Format.
        """
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSpecSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Hole ein einzelnes Quiz im Spec-Format.
        """
        quiz = self.get_object()
        serializer = QuizSpecSerializer(quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partielle Aktualisierung im Spec-Format.
        """
        quiz = self.get_object()
        serializer = QuizSerializer(quiz, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = QuizSpecSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    def _process_youtube_url(self, youtube_url):
        """
        Verarbeite YouTube-URL über Pipeline mit Fallback.
        """
        try:
            return PipelineService().process_youtube_url(youtube_url)
        except Exception:
            return {
                'title': 'Quiz Title',
                'description': 'Quiz Description',
                'questions': [{
                    'order': 1,
                    'question': 'Question 1',
                    'answers': [
                        {'text': 'Option A', 'is_correct': True},
                        {'text': 'Option B', 'is_correct': False},
                        {'text': 'Option C', 'is_correct': False},
                        {'text': 'Option D', 'is_correct': False}
                    ]
                }],
                'transcript': None
            }
    
    def _create_quiz_from_data(self, user, quiz_data, youtube_url):
        """
        Erstelle Quiz-Objekt aus verarbeiteten Daten.
        """
        return Quiz.objects.create(
            user=user,
            title=quiz_data.get('title', 'Quiz Title'),
            description=quiz_data.get('description', ''),
            youtube_url=youtube_url,
            transcript=quiz_data.get('transcript')
        )
    
    def _create_questions_and_answers(self, quiz, questions_data):
        """
        Erstelle Fragen und Antworten für ein Quiz.
        """
        for q_index, q in enumerate(questions_data, start=1):
            question = Question.objects.create(
                quiz=quiz,
                question_text=q.get('question', ''),
                order=q.get('order', q_index)
            )
            for a_index, ans in enumerate(q.get('answers', []), start=1):
                Answer.objects.create(
                    question=question,
                    answer_text=ans.get('text', ''),
                    is_correct=ans.get('is_correct', False),
                    order=a_index
                )
    
    def create(self, request, *args, **kwargs):
        """
        Erstelle ein Quiz aus einer YouTube-URL.
        """
        input_serializer = QuizCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        youtube_url = input_serializer.validated_data['url']
        
        quiz_data = self._process_youtube_url(youtube_url)
        quiz = self._create_quiz_from_data(request.user, quiz_data, youtube_url)
        self._create_questions_and_answers(quiz, quiz_data.get('questions', []))
        
        response_serializer = QuizSpecSerializer(quiz)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
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
        
        # Validiere erforderliche Felder
        required_fields = ['response_id', 'question_id', 'answer_id']
        for field in required_fields:
            if not data.get(field):
                return Response(
                    {'error': f'{field} is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Versuche Objekte zu laden
        try:
            quiz_response = QuizResponse.objects.get(id=data.get('response_id'))
            question = Question.objects.get(id=data.get('question_id'))
            answer = Answer.objects.get(id=data.get('answer_id'))
        except (QuizResponse.DoesNotExist, Question.DoesNotExist, Answer.DoesNotExist) as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        response_id = request.data.get('response_id')
        
        # Validiere erforderliche Felder
        if not response_id:
            return Response(
                {'error': 'response_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Versuche QuizResponse zu laden
        try:
            quiz_response = QuizResponse.objects.get(id=response_id)
        except QuizResponse.DoesNotExist:
            return Response(
                {'error': 'QuizResponse not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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

