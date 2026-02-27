from django.db import models
from users.models import CustomUser


class Quiz(models.Model):
    """
    Quiz Model - Hauptmodell für Quizzes.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    youtube_url = models.URLField()
    transcript = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """
    Question Model - Fragen im Quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    """
    Answer Model - Antwortmöglichkeiten für Fragen.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.answer_text[:30]}"


class QuizResponse(models.Model):
    """
    QuizResponse Model - Benutzersession beim Quiz spielen.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='quiz_responses')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='responses')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}"


class UserAnswer(models.Model):
    """
    UserAnswer Model - Benutzerantworten pro Frage.
    """
    quiz_response = models.ForeignKey(QuizResponse, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.SET_NULL, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['question__order']
    
    def __str__(self):
        return f"{self.quiz_response} - Q{self.question.order}"
