"""Serializers used by quiz API endpoints."""

from rest_framework import serializers

from quizzes.models import Answer, Question, Quiz, QuizResponse, UserAnswer


class AnswerSerializer(serializers.ModelSerializer):
    """Serialize quiz answer choices."""

    class Meta:
        model = Answer
        fields = ["id", "answer_text", "order", "is_correct"]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize quiz questions including answers."""

    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "order", "answers"]
        read_only_fields = ["id"]


class QuizSerializer(serializers.ModelSerializer):
    """Serialize quiz overview data."""

    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "youtube_url", "created_at", "question_count"]
        read_only_fields = ["id", "created_at"]

    def get_question_count(self, obj):
        """Return number of questions in quiz."""
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    """Serialize full quiz details with questions and answers."""

    questions = QuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "youtube_url",
            "transcript",
            "questions",
            "question_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "transcript", "created_at"]

    def get_question_count(self, obj):
        """Return number of questions in quiz."""
        return obj.questions.count()


class UserAnswerSerializer(serializers.ModelSerializer):
    """Serialize answers submitted by users."""

    answer_text = serializers.CharField(source="selected_answer.answer_text", read_only=True)
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = ["id", "question", "selected_answer", "answer_text", "is_correct", "answered_at"]
        read_only_fields = ["id", "answered_at"]

    def get_is_correct(self, obj):
        """Return whether selected answer is correct."""
        return bool(obj.selected_answer and obj.selected_answer.is_correct)


class QuizResponseSerializer(serializers.ModelSerializer):
    """Serialize quiz session progress and score."""

    answers = UserAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = QuizResponse
        fields = ["id", "quiz", "started_at", "completed_at", "score", "answers"]
        read_only_fields = ["id", "started_at"]


class QuizCreateSerializer(serializers.Serializer):
    """Validate payload for quiz creation from YouTube URL."""

    url = serializers.URLField()


class QuizSpecQuestionSerializer(serializers.ModelSerializer):
    """Serialize question payload in the expected frontend-compatible format."""

    question_title = serializers.CharField(source="question_text")
    question_options = serializers.SerializerMethodField()
    answer = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "question_title", "question_options", "answer", "created_at", "updated_at"]

    def get_question_options(self, obj):
        """Return ordered question options."""
        return [answer.answer_text for answer in obj.answers.all()]

    def get_answer(self, obj):
        """Return the correct answer text if available."""
        correct = obj.answers.filter(is_correct=True).first()
        return correct.answer_text if correct else ""

    def get_created_at(self, obj):
        """Expose creation timestamp."""
        return obj.created_at

    def get_updated_at(self, obj):
        """Expose update timestamp placeholder for schema compatibility."""
        return obj.created_at


class QuizSpecSerializer(serializers.ModelSerializer):
    """Serialize quiz payload in the expected API format."""

    video_url = serializers.CharField(source="youtube_url")
    questions = QuizSpecQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "created_at", "updated_at", "video_url", "questions"]
