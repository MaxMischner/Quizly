"""
Custom JWT authentication that reads the access token from HTTP-only cookies.
"""
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate using the access token stored in the access_token cookie.
    """

    def authenticate(self, request):
        # Keep Bearer-token compatibility for tests and API clients.
        header_auth = super().authenticate(request)
        if header_auth is not None:
            return header_auth

        cookie_name = getattr(settings, "JWT_ACCESS_COOKIE_NAME", "access_token")
        raw_token = request.COOKIES.get(cookie_name)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None
