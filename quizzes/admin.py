"""
Admin Interface für Quiz-Management.
"""
from django.contrib import admin
from quizzes.models import Quiz, Question, Answer, QuizResponse, UserAnswer


class AnswerInline(admin.TabularInline):
    """
    Inline-Admin für Answers innerhalb einer Question.
    """
    model = Answer
    extra = 1
    fields = ['answer_text', 'is_correct', 'order']


class QuestionInline(admin.StackedInline):
    """
    Inline-Admin für Questions innerhalb eines Quiz.
    """
    model = Question
    extra = 1
    fields = ['question_text', 'order']
    inlines = [AnswerInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Quiz-Verwaltung.
    Erlaubt das Bearbeiten von Titel, Beschreibung und Fragen.
    """
    list_display = ['title', 'user', 'created_at', 'question_count']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'transcript']
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basis-Info', {'fields': ('title', 'description', 'user')}),
        ('YouTube', {'fields': ('youtube_url',)}),
        ('Transkript', {'fields': ('transcript',), 'classes': ('collapse',)}),
        ('Zeitstempel', {'fields': ('created_at', 'updated_at')}),
    )
    
    def question_count(self, obj):
        """
        Zeige die Anzahl der Fragen im Quiz.
        """
        return obj.questions.count()
    question_count.short_description = 'Anzahl Fragen'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Quiz-Fragen.
    """
    list_display = ['quiz', 'order', 'question_text', 'answer_count']
    list_filter = ['quiz', 'order']
    search_fields = ['question_text', 'quiz__title']
    inlines = [AnswerInline]
    
    def answer_count(self, obj):
        """
        Zeige die Anzahl der Antworten.
        """
        return obj.answers.count()
    answer_count.short_description = 'Anzahl Antworten'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Antwortmöglichkeiten.
    """
    list_display = ['question', 'order', 'answer_text', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['answer_text', 'question__question_text']
    readonly_fields = ['question']


@admin.register(QuizResponse)
class QuizResponseAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Quiz-Spielsessions.
    """
    list_display = ['user', 'quiz', 'started_at', 'score', 'status']
    list_filter = ['started_at', 'completed_at', 'quiz']
    search_fields = ['user__username', 'quiz__title']
    readonly_fields = ['started_at', 'user', 'quiz']
    
    def status(self, obj):
        """
        Zeige ob Quiz abgeschlossen ist.
        """
        return 'Abgeschlossen' if obj.completed_at else 'In Bearbeitung'
    status.short_description = 'Status'


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """
    Admin-Interface für Benutzerantworten.
    """
    list_display = ['quiz_response', 'question', 'selected_answer', 'is_correct']
    list_filter = ['question__quiz', 'answered_at']
    search_fields = ['quiz_response__user__username']
    readonly_fields = ['answered_at', 'quiz_response', 'question']
    
    def is_correct(self, obj):
        """
        Zeige ob die Antwort korrekt ist.
        """
        if obj.selected_answer:
            return obj.selected_answer.is_correct
        return 'Nicht beantwortet'
    is_correct.short_description = 'Korrekt'

