from django.db import models
from users.models import CustomUser


class Quiz(models.Model):
    """Main model representing a generated quiz."""
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
    """Question belonging to a quiz."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class Answer(models.Model):
    """Answer option for a question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.answer_text[:30]}"
