"""
Views für User-Management und Authentifizierung.
"""
from rest_framework import status, views, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import authenticate
from users.models import CustomUser, TokenBlacklist
from users.serializers import UserSerializer, RegisterSerializer, LoginSerializer


class RegisterView(views.APIView):
    """
    API Endpoint für Benutzerregistrierung.
    POST /api/register/
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
                {'detail': 'User created successfully!'},
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
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if user is not None:
            refresh = RefreshToken.for_user(user)
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
            response = Response({
                'detail': 'Login successfully!',
                'user': user_data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
            response.set_cookie('access_token', str(refresh.access_token), 
                              httponly=True, secure=False, samesite='Lax')
            response.set_cookie('refresh_token', str(refresh), 
                              httponly=True, secure=False, samesite='Lax')
            return response
        
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(views.APIView):
    """
    API Endpoint für Benutzer-Logout.
    POST /api/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Logout Benutzer und blackliste den Refresh Token.
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                TokenBlacklist.objects.create(token=refresh_token)
        except Exception:
            pass
        
        response = Response({
            'detail': 'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'
        }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class TokenRefreshView(views.APIView):
    """
    API Endpoint für Token-Erneuerung.
    POST /api/token/refresh/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Erneuere den Access Token mithilfe des Refresh Tokens.
        """
        # Versuche, Refresh Token aus Cookies oder Request Body zu holen
        refresh_token = None
        
        # Prüfe zuerst in Cookies
        if 'refresh_token' in request.COOKIES:
            refresh_token = request.COOKIES.get('refresh_token')
        # Falls nicht in Cookies, prüfe in Request Body
        elif 'refresh' in request.data:
            refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response(
                {'detail': 'No refresh token provided'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            
            response = Response({
                'detail': 'Token refreshed',
                'access': new_access_token,
            }, status=status.HTTP_200_OK)
            
            # Setze neuen Access Token Cookie
            response.set_cookie('access_token', new_access_token,
                              httponly=True, secure=False, samesite='Lax')
            
            return response
        except (InvalidToken, TokenError):
            return Response(
                {'detail': 'Invalid refresh token'},
                status=status.HTTP_401_UNAUTHORIZED
            )


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

