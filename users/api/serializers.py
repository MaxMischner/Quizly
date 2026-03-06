"""Serializers used by user API endpoints."""

from rest_framework import serializers

from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Serialize authenticated user profile data."""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "first_name", "last_name", "created_at"]
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """Validate and create users during registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "confirmed_password"]

    def validate(self, data):
        """Validate matching passwords and unique email."""
        if data["password"] != data.pop("confirmed_password"):
            raise serializers.ValidationError("Passwoerter stimmen nicht ueberein")

        if CustomUser.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError("Diese E-Mail ist bereits registriert")

        return data

    def create(self, validated_data):
        """Create a user with hashed password handling."""
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate the login payload."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
