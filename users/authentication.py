"""
Custom JWT authentication that reads the access token from HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class CookieJWTAuthentication(JWTAuthentication):
    """
    Authenticate using the access token stored in the access_token cookie.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None  # No authentication, let other methods or AllowAny handle it

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            return None  # Invalid token, but don't block the request
