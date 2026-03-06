"""Compatibility module that re-exports user API views."""

from users.api.views import LoginView, LogoutView, RegisterView, TokenRefreshView, UserProfileView

__all__ = [
    "RegisterView",
    "LoginView",
    "LogoutView",
    "TokenRefreshView",
    "UserProfileView",
]

