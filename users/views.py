"""
Views für User-Management und Authentifizierung.
"""
from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from users.models import CustomUser, TokenBlacklist
from users.serializers import UserSerializer, RegisterSerializer, LoginSerializer


class RegisterView(views.APIView):
    """
    API Endpoint für Benutzerregistrierung.
    POST /api/users/register/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Registriere einen neuen Benutzer.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Registrierung erfolgreich'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    """
    API Endpoint für Benutzer-Login mit JWT.
    POST /api/users/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authentifiziere Benutzer und gebe JWT Tokens zurück.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            response = Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(refresh.access_token), 
                              httponly=True, secure=True, samesite='Strict')
            response.set_cookie('refresh_token', str(refresh), 
                              httponly=True, secure=True, samesite='Strict')
            return response
        
        return Response(
            {'detail': 'Ungültige Anmeldedaten'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(views.APIView):
    """
    API Endpoint für Benutzer-Logout.
    POST /api/users/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout Benutzer und blackliste den Refresh Token.
        """
        refresh_token = request.data.get('refresh')
        if refresh_token:
            TokenBlacklist.objects.create(token=refresh_token)
        
        response = Response({
            'detail': 'Abmeldung erfolgreich'
        }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class UserProfileView(views.APIView):
    """
    API Endpoint für User-Profil.
    GET /api/users/profile/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Hole das Profil des eingeloggten Users.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

