"""
Serializer für Quiz-Management und Spielteilnahme.
"""
from rest_framework import serializers
from quizzes.models import Quiz, Question, Answer, QuizResponse, UserAnswer


class AnswerSerializer(serializers.ModelSerializer):
    """
    Serializer für Antwortmöglichkeiten.
    is_correct wird bei Detail-Ansicht versteckt.
    """
    class Meta:
        model = Answer
        fields = ['id', 'answer_text', 'order', 'is_correct']
        read_only_fields = ['id']


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer für Quiz-Fragen mit Antworten.
    """
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'order', 'answers']
        read_only_fields = ['id']


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer für Quiz-Übersicht.
    Zeigt nur wichtige Informationen.
    """
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'youtube_url', 'created_at', 'question_count']
        read_only_fields = ['id', 'created_at']
    
    def get_question_count(self, obj):
        """
        Zähle die Anzahl der Fragen.
        """
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    """
    Serializer für Quiz-Detail-Ansicht.
    Zeigt alle Fragen und Antworten.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'youtube_url', 'transcript', 'questions', 'question_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'transcript', 'created_at']
    
    def get_question_count(self, obj):
        """
        Zähle die Anzahl der Fragen.
        """
        return obj.questions.count()


class UserAnswerSerializer(serializers.ModelSerializer):
    """
    Serializer für Benutzerantworten.
    """
    answer_text = serializers.CharField(source='selected_answer.answer_text', read_only=True)
    is_correct = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAnswer
        fields = ['id', 'question', 'selected_answer', 'answer_text', 'is_correct', 'answered_at']
        read_only_fields = ['id', 'answered_at']
    
    def get_is_correct(self, obj):
        """
        Prüfe ob die Antwort korrekt ist.
        """
        if obj.selected_answer:
            return obj.selected_answer.is_correct
        return False


class QuizResponseSerializer(serializers.ModelSerializer):
    """
    Serializer für Quiz-Spielsession.
    """
    answers = UserAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizResponse
        fields = ['id', 'quiz', 'started_at', 'completed_at', 'score', 'answers']
        read_only_fields = ['id', 'started_at']


class QuizCreateSerializer(serializers.Serializer):
    """
    Input-Serializer für Quiz-Erstellung via YouTube-URL.
    """
    url = serializers.URLField()


class QuizSpecQuestionSerializer(serializers.ModelSerializer):
    """
    Spec-Serializer für Quiz-Fragen im API-Format.
    """
    question_title = serializers.CharField(source='question_text')
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

    def get_question_options(self, obj):
        return [a.answer_text for a in obj.answers.all()]

    def get_answer(self, obj):
        correct = obj.answers.filter(is_correct=True).first()
        return correct.answer_text if correct else ''

    def get_created_at(self, obj):
        return obj.created_at

    def get_updated_at(self, obj):
        # Question hat kein updated_at Feld, nutze created_at.
        return obj.created_at


class QuizSpecSerializer(serializers.ModelSerializer):
    """
    Spec-Serializer für Quiz-Ausgaben.
    """
    video_url = serializers.CharField(source='youtube_url')
    questions = QuizSpecQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
