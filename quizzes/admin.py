"""Admin configuration for quiz management."""
from django.contrib import admin
from quizzes.models import Quiz, Question, Answer, UserAnswer


class AnswerInline(admin.TabularInline):
    """Inline admin for answers inside a question."""
    model = Answer
    extra = 1
    fields = ['answer_text', 'is_correct', 'order']


class QuestionInline(admin.StackedInline):
    """Inline admin for questions inside a quiz."""
    model = Question
    extra = 1
    fields = ['question_text', 'order']
    inlines = [AnswerInline]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin configuration for quiz records and nested content."""
    list_display = ['title', 'user', 'created_at', 'question_count']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'transcript']
    inlines = [QuestionInline]
    
    fieldsets = (
        ("Basic", {"fields": ("title", "description", "user")}),
        ("YouTube", {"fields": ("youtube_url",)}),
        ("Transcript", {"fields": ("transcript",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    
    def question_count(self, obj):
        """Return number of questions for this quiz."""
        return obj.questions.count()
    question_count.short_description = "Question count"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin configuration for quiz questions."""
    list_display = ['quiz', 'order', 'question_text', 'answer_count']
    list_filter = ['quiz', 'order']
    search_fields = ['question_text', 'quiz__title']
    inlines = [AnswerInline]
    
    def answer_count(self, obj):
        """Return number of answers for this question."""
        return obj.answers.count()
    answer_count.short_description = "Answer count"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin configuration for question answers."""
    list_display = ['question', 'order', 'answer_text', 'is_correct']
    list_filter = ['is_correct', 'question__quiz']
    search_fields = ['answer_text', 'question__question_text']
    readonly_fields = ['question']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Admin configuration for user answers."""
    list_display = ['quiz_response', 'question', 'selected_answer', 'is_correct']
    list_filter = ['question__quiz', 'answered_at']
    search_fields = ['quiz_response__user__username']
    readonly_fields = ['answered_at', 'quiz_response', 'question']
    
    def is_correct(self, obj):
        """Return answer correctness in admin list view."""
        if obj.selected_answer:
            return obj.selected_answer.is_correct
        return "Not answered"
    is_correct.short_description = "Correct"

