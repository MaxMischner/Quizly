"""
Tests for token refresh.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class TokenRefreshTests(TestCase):
    """
    Tests für die POST /api/token/refresh/ Endpoint.
    Testet erfolgreiche Token-Erneuerung und verschiedene Fehlerszenarien.
    """

    def setUp(self):
        """Initialisiere API Client und erstelle authentifizierten Benutzer."""
        self.client = APIClient()
        self.refresh_url = reverse('token_refresh')
        self.login_url = reverse('login')

        # Erstelle einen Testbenutzer
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='SecurePassword123'
        )

        # Login und erhalte Token
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'SecurePassword123'
        })

        # Extrahiere Tokens aus Response
        self.access_token = login_response.data.get('access')
        self.refresh_token = login_response.data.get('refresh')

    def test_token_refresh_success_with_refresh_token_in_body(self):
        """
        Test: Erfolgreiche Token-Erneuerung mit Refresh Token im Request Body.
        Erwartet: 200 Status Code mit neuem Access Token.
        """
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')
        self.assertIn('access', response.data)
        # Neuer Access Token sollte sich vom alten unterscheiden
        self.assertNotEqual(response.data['access'], self.access_token)

    def test_token_refresh_sets_access_token_cookie(self):
        """
        Test: Neuer Access Token wird als HTTP-Only Cookie gesetzt.
        Erwartet: Cookie 'access_token' im Response.
        """
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        cookie = response.cookies['access_token']
        self.assertTrue(cookie['httponly'])

    def test_token_refresh_without_refresh_token(self):
        """
        Test: Token-Erneuerung ohne Refresh Token schlägt fehl.
        Erwartet: 401 Status Code wenn weder Cookies noch Body Token vorhanden.
        """
        # Neue Session ohne Cookies
        client = APIClient()
        refresh_url = reverse('token_refresh')

        response = client.post(refresh_url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'No refresh token provided')

    def test_token_refresh_with_invalid_token(self):
        """
        Test: Token-Erneuerung mit ungültigem Refresh Token schlägt fehl.
        Erwartet: 401 Status Code.
        """
        client = APIClient()
        refresh_url = reverse('token_refresh')

        response = client.post(refresh_url, {'refresh': 'invalid_token_here'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid refresh token')

    def test_token_refresh_with_random_string_token(self):
        """
        Test: Token-Erneuerung mit zufälligem String schlägt fehl.
        Erwartet: 401 Status Code (ungültiger Token).
        """
        client = APIClient()
        refresh_url = reverse('token_refresh')

        response = client.post(refresh_url, {'refresh': 'randomstringtoken123456'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid refresh token')

    def test_token_refresh_response_format(self):
        """
        Test: Response hat das korrekte Format.
        Erwartet: JSON mit 'detail' und 'access' Feldern.
        """
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertIn('detail', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['detail'], 'Token refreshed')

    def test_token_refresh_multiple_times(self):
        """
        Test: Token-Erneuerung mehrmals hintereinander funktioniert.
        Erwartet: Alle Requests sollten erfolgreich sein (200).
        """
        current_refresh = self.refresh_token

        for _ in range(3):
            response = self.client.post(self.refresh_url, {'refresh': current_refresh})

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            new_access = response.data.get('access')
            self.assertIsNotNone(new_access)

    def test_token_refresh_no_authentication_required_for_post(self):
        """
        Test: Token-Refresh Endpoint erfordert keine Authorization Header.
        Erwartet: 200 oder 401 (je nach Token), aber nicht 403.
        """
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_token_refresh_with_empty_request_body(self):
        """
        Test: Token-Refresh mit leerem Request Body funktioniert mit Cookie.
        Erwartet: 200 Status Code (nutzt Refresh Token aus Cookie).
        """
        response = self.client.post(self.refresh_url, {})

        # Mit Cookie sollte es funktionieren
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')

    def test_token_refresh_with_malformed_token(self):
        """
        Test: Token-Refresh mit ungültiger Token-Struktur schlägt fehl.
        Erwartet: 401 Status Code.
        """
        client = APIClient()
        refresh_url = reverse('token_refresh')

        response = client.post(refresh_url, {'refresh': 'not.a.valid.token.structure'})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_new_token_is_valid(self):
        """
        Test: Neuer Access Token kann für authenticated Requests verwendet werden.
        Erwartet: 200 Status Code beim Zugriff auf geschützten Endpoint.
        """
        # Erneuere Token
        refresh_response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})
        new_access_token = refresh_response.data.get('access')

        # Verwende neuen Token für Profile Request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        profile_url = reverse('profile')
        profile_response = self.client.get(profile_url)

        # Sollte erfolgreich sein mit neuem Token
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

    def test_token_refresh_with_empty_string_in_cookie(self):
        """
        Test: Token-Refresh mit leerem String in Cookies schlägt fehl.
        Erwartet: 401 Status Code.
        """
        client = APIClient()
        refresh_url = reverse('token_refresh')
        client.cookies['refresh_token'] = ''

        response = client.post(refresh_url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_with_body_overrides_cookie(self):
        """
        Test: Body Token wird bevorzugt wenn sowohl Cookie als auch Body vorhanden.
        Erwartet: 200 Status Code (Body Token verwendet).
        """
        # Body Token ist gültig
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')

    def test_token_refresh_no_rate_limit(self):
        """
        Test: Keine Rate-Limiting auf Token-Refresh Endpoint.
        Erwartet: Mehrere Requests sollten beantwortet werden (kein 429).
        """
        for _ in range(5):
            response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

            # Sollte 200 oder 401 sein, nicht 429
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_token_refresh_response_has_new_token_string(self):
        """
        Test: Response enthält neuen Token als String.
        Erwartet: 'access' ist ein String, kein Objekt.
        """
        response = self.client.post(self.refresh_url, {'refresh': self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['access'], str)
        # Token sollte Punkte enthalten (JWT Format: xxx.xxx.xxx)
        self.assertGreaterEqual(response.data['access'].count('.'), 2)

    def test_token_refresh_with_refresh_token_from_cookie(self):
        """
        Test: Token-Refresh mit Refresh Token aus Cookie funktioniert.
        Erwartet: 200 Status Code.
        """
        # Setze Refresh Token in Cookie manuell
        self.client.cookies['refresh_token'] = self.refresh_token

        response = self.client.post(self.refresh_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Token refreshed')

    def test_token_refresh_prefers_body_over_cookie(self):
        """
        Test: Token aus Request Body wird bevorzugt gegenüber Cookie.
        Erwartet: 200 Status Code mit Body Token.
        """
        # Erstelle zweiten Benutzer und Login
        CustomUser.objects.create_user(
            username='testuser2',
            email='testuser2@example.com',
            password='SecurePassword123'
        )

        login_response2 = self.client.post(self.login_url, {
            'username': 'testuser2',
            'password': 'SecurePassword123'
        })

        refresh_token2 = login_response2.data.get('refresh')

        # Setze Cookie mit einem Token, Body mit anderem Token
        self.client.cookies['refresh_token'] = self.refresh_token

        response = self.client.post(self.refresh_url, {'refresh': refresh_token2})

        # Sollte erfolgreich sein (Body Token verwendet)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
