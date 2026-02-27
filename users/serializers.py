"""
Serializer für User-Management und Authentifizierung.
"""
from rest_framework import serializers
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer für CustomUser - Profil-Ansicht.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer für Benutzerregistrierung.
    Validiert Passwörter und eindeutige E-Mail.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'confirmed_password']
    
    def validate(self, data):
        """
        Validiere Passwort-Übereinstimmung und E-Mail-Eindeutigkeit.
        """
        if data['password'] != data.pop('confirmed_password'):
            msg = 'Passwörter stimmen nicht überein'
            raise serializers.ValidationError(msg)
        
        if CustomUser.objects.filter(email=data['email']).exists():
            msg = 'Diese E-Mail ist bereits registriert'
            raise serializers.ValidationError(msg)
        
        return data
    
    def create(self, validated_data):
        """
        Erstelle einen neuen Benutzer mit gehashedtem Passwort.
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer für Login-Validierung.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
