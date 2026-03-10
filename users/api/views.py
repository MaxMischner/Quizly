"""Views responsible for user management and authentication."""

from django.conf import settings
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from users.models import TokenBlacklist


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str | None = None) -> None:
    """Set auth cookies with environment-aware security flags."""
    access_cookie_name = getattr(settings, "JWT_ACCESS_COOKIE_NAME", "access_token")
    refresh_cookie_name = getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh_token")

    response.set_cookie(
        access_cookie_name,
        access_token,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        domain=settings.JWT_COOKIE_DOMAIN,
        path="/",
    )
    if refresh_token:
        response.set_cookie(
            refresh_cookie_name,
            refresh_token,
            httponly=True,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            domain=settings.JWT_COOKIE_DOMAIN,
            path="/",
        )


class RegisterView(views.APIView):
    """Register a new user account."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle user registration requests."""
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    """Authenticate users and issue JWT tokens."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle login and set token cookies for browser clients."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        access_lifetime_seconds = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())
        refresh_lifetime_seconds = int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds())
        user_data = {"id": user.id, "username": user.username, "email": user.email}
        response = Response(
            {
                "detail": "Login successfully!",
                "user": user_data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )
        _set_auth_cookies(response, str(refresh.access_token), str(refresh))
        return response


class LogoutView(views.APIView):
    """Logout authenticated users and invalidate refresh tokens."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist provided refresh token and clear auth cookies."""
        refresh_token = request.data.get("refresh") or request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                TokenBlacklist.objects.create(token=refresh_token)
            except Exception:
                pass

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie(
            settings.JWT_ACCESS_COOKIE_NAME,
            domain=settings.JWT_COOKIE_DOMAIN,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )
        response.delete_cookie(
            settings.JWT_REFRESH_COOKIE_NAME,
            domain=settings.JWT_COOKIE_DOMAIN,
            path="/",
            samesite=settings.JWT_COOKIE_SAMESITE,
        )
        return response


class TokenRefreshView(views.APIView):
    """Issue a new access token from a refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Refresh access token from request body or cookies."""
        refresh_token = request.data.get("refresh") or request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response({"detail": "No refresh token provided"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            if TokenBlacklist.objects.filter(token=refresh_token).exists():
                return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            response = Response({"detail": "Token refreshed", "access": new_access_token}, status=status.HTTP_200_OK)
            _set_auth_cookies(response, new_access_token)
            return response
        except (InvalidToken, TokenError):
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class UserProfileView(views.APIView):
    """Return the profile of the authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Handle profile retrieval requests."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
