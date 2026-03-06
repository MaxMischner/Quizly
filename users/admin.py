"""Admin configuration for user management."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, TokenBlacklist


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom users."""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    """Admin configuration for blacklisted tokens."""
    list_display = ['token', 'blacklisted_at']
    list_filter = ['blacklisted_at']
    search_fields = ['token']
    readonly_fields = ['blacklisted_at']

