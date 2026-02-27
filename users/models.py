from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom User Model mit zusätzlichen Feldern.
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username


class TokenBlacklist(models.Model):
    """
    Token Blacklist für ausgeloggte Tokens.
    """
    token = models.TextField(unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Blacklisted token {self.token[:20]}..."
