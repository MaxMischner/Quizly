"""
Tests for user login.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class UserLoginTests(TestCase):
    """
    Tests für die POST /api/login/ Endpoint.
    Testet erfolgreiche Anmeldung und verschiedene Fehlerszenarien.
    """

    def setUp(self):
        """Initialisiere API Client und erstelle Testbenutzer."""
        self.client = APIClient()
        self.login_url = reverse('login')

        # Erstelle einen Testbenutzer
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'SecurePassword123'
        }

        self.user = CustomUser.objects.create_user(**self.user_data)

        # Login-Daten für Tests
        self.valid_login_data = {
            'username': 'testuser',
            'password': 'SecurePassword123'
        }

    def test_login_success(self):
        """
        Test: Erfolgreicher Login mit gültigen Anmeldedaten.
        Erwartet: 200 Status Code mit User-Info und "Login successfully!" Nachricht.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Login successfully!')
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'testuser@example.com')
        self.assertEqual(response.data['user']['id'], self.user.id)

    def test_login_sets_access_token_cookie(self):
        """
        Test: Access Token wird als HTTP-Only Cookie gesetzt.
        Erwartet: Cookie 'access_token' im Response.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.cookies)
        cookie = response.cookies['access_token']
        self.assertTrue(cookie['httponly'])

    def test_login_sets_refresh_token_cookie(self):
        """
        Test: Refresh Token wird als HTTP-Only Cookie gesetzt.
        Erwartet: Cookie 'refresh_token' im Response.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh_token', response.cookies)
        cookie = response.cookies['refresh_token']
        self.assertTrue(cookie['httponly'])

    def test_login_invalid_password(self):
        """
        Test: Login mit falshem Passwort schlägt fehl.
        Erwartet: 401 Status Code.
        """
        data = self.valid_login_data.copy()
        data['password'] = 'WrongPassword123'

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    def test_login_nonexistent_user(self):
        """
        Test: Login für nicht existierenden Benutzer schlägt fehl.
        Erwartet: 401 Status Code.
        """
        data = {
            'username': 'nonexistent',
            'password': 'SomePassword123'
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_username(self):
        """
        Test: Login ohne Username schlägt fehl.
        Erwartet: 401 Status Code mit Error.
        """
        data = {'password': 'SecurePassword123'}

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('username', response.data)

    def test_login_missing_password(self):
        """
        Test: Login ohne Passwort schlägt fehl.
        Erwartet: 401 Status Code mit Error.
        """
        data = {'username': 'testuser'}

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('password', response.data)

    def test_login_empty_username(self):
        """
        Test: Login mit leerem Username schlägt fehl.
        Erwartet: 401 Status Code.
        """
        data = {
            'username': '',
            'password': 'SecurePassword123'
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_empty_password(self):
        """
        Test: Login mit leerem Passwort schlägt fehl.
        Erwartet: 401 Status Code.
        """
        data = {
            'username': 'testuser',
            'password': ''
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_case_sensitive_username(self):
        """
        Test: Username ist case-sensitive.
        Erwartet: 401 wenn falscher Case verwendet wird.
        """
        data = {
            'username': 'TestUser',  # unterschiedlicher Case
            'password': 'SecurePassword123'
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_response_format(self):
        """
        Test: Response hat das korrekte Format.
        Erwartet: JSON mit 'detail' und 'user' Feldern.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertIn('detail', response.data)
        self.assertIn('user', response.data)
        self.assertIn('id', response.data['user'])
        self.assertIn('username', response.data['user'])
        self.assertIn('email', response.data['user'])

    def test_login_password_not_in_response(self):
        """
        Test: Passwort wird nicht in Response zurückgesendet.
        Sicherheit: Passwort sollte niemals sichtbar sein.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertNotIn('password', response.data)
        self.assertNotIn('password', response.data.get('user', {}))

    def test_login_no_authentication_required(self):
        """
        Test: Login Endpoint erfordert keine Authentifizierung.
        Erwartet: 200 oder 401 (je nach Daten), aber nicht 403 Forbidden.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_after_registration(self):
        """
        Test: Benutzer kann sich nach erfolgreicher Registrierung anmelden.
        Erwartet: 200 Status Code.
        """
        # Registriere neuen Benutzer
        register_url = reverse('register')
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'NewPassword123',
            'confirmed_password': 'NewPassword123'
        }

        register_response = self.client.post(register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # Versuche, sich anzumelden
        login_data = {
            'username': 'newuser',
            'password': 'NewPassword123'
        }

        login_response = self.client.post(self.login_url, login_data)

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data['user']['username'], 'newuser')

    def test_login_special_characters_in_password(self):
        """
        Test: Login mit Sonderzeichen im Passwort funktioniert.
        Erwartet: 200 Status Code.
        """
        special_password = 'P@$sw0rd!#%'
        CustomUser.objects.create_user(
            username='specialuser',
            email='special@example.com',
            password=special_password
        )

        data = {
            'username': 'specialuser',
            'password': special_password
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'specialuser')

    def test_login_returns_user_id(self):
        """
        Test: Response enthält die User ID.
        Erwartet: User ID im Response data.
        """
        response = self.client.post(self.login_url, self.valid_login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['id'], self.user.id)

    def test_login_multiple_attempts(self):
        """
        Test: Mehrere Login-Versuche funktionieren (no rate limiting).
        Erwartet: Alle Anfragen sollten beantwortet werden (kein 429).
        """
        for _ in range(3):
            response = self.client.post(self.login_url, self.valid_login_data)
            # Sollte kein Rate Limiting geben
            self.assertNotEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_wrong_username_case(self):
        """
        Test: Login mit falscher Username-Schreibweise schlägt fehl.
        Erwartet: 401 Status Code.
        """
        data = {
            'username': 'TestUser',  # falscher Case
            'password': 'SecurePassword123'
        }

        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Invalid credentials')
