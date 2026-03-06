"""Compatibility module that re-exports user API serializers."""

from users.api.serializers import LoginSerializer, RegisterSerializer, UserSerializer

__all__ = ["UserSerializer", "RegisterSerializer", "LoginSerializer"]
