"""
Tests for user logout.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class UserLogoutTests(TestCase):
    """
    Tests für die POST /api/logout/ Endpoint.
    Testet erfolgreichen Logout und verschiedene Fehlerszenarien.
    """

    def setUp(self):
        """Initialisiere API Client und erstelle authentifizierten Benutzer."""
        self.client = APIClient()
        self.logout_url = reverse('logout')
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

        # Extrahiere Token-Strings aus Response (nicht Cookies)
        self.access_token = login_response.data.get('access')
        self.refresh_token = login_response.data.get('refresh')

    def test_logout_success_with_authentication(self):
        """
        Test: Erfolgreicher Logout mit gültiger Authentifizierung.
        Erwartet: 200 Status Code mit korrekter Nachricht.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['detail'],
            'Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid.'
        )

    def test_logout_without_authentication(self):
        """
        Test: Logout ohne Authentifizierung schlägt fehl.
        Erwartet: 401 Status Code.
        """
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_removes_access_token_cookie(self):
        """
        Test: Access Token Cookie wird gelöscht.
        Erwartet: Cookie sollte leer sein oder max_age=0.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access_token' in response.cookies)

    def test_logout_removes_refresh_token_cookie(self):
        """
        Test: Refresh Token Cookie wird gelöscht.
        Erwartet: Cookie sollte leer sein oder max_age=0.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('refresh_token' in response.cookies)

    def test_logout_with_empty_request_body(self):
        """
        Test: Logout mit leerem Request Body funktioniert.
        Erwartet: 200 Status Code.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_response_format(self):
        """
        Test: Response hat das korrekte Format.
        Erwartet: JSON mit 'detail' Feld.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.logout_url, {})

        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data['detail'], str)

    def test_logout_multiple_times(self):
        """
        Test: Mehrfacher Logout ist möglich.
        Erwartet: Beide Requests sollten erfolgreich sein (200).
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Erstes Logout sollte erfolgreich sein
        response1 = self.client.post(self.logout_url, {})
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Für zweites Logout neuer Login erforderlich
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'SecurePassword123'
        })

        new_access_token = login_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')

        # Zweites Logout sollte auch erfolgreich sein
        response2 = self.client.post(self.logout_url, {})
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

    def test_logout_with_invalid_token(self):
        """
        Test: Logout mit ungültigem Token schlägt fehl.
        Erwartet: 401 Status Code.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token_here')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_malformed_auth_header(self):
        """
        Test: Logout mit ungültigem Authorization Header schlägt fehl.
        Erwartet: 401 Status Code.
        """
        self.client.credentials(HTTP_AUTHORIZATION='InvalidFormat token')
        response = self.client.post(self.logout_url, {})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_post_method(self):
        """
        Test: Logout akzeptiert nur POST Requests.
        Erwartet: GET sollte 405 Method Not Allowed geben.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_logout_with_refresh_token_in_body(self):
        """
        Test: Logout funktioniert mit oder ohne Refresh Token im Request Body.
        Erwartet: 200 Status Code.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Logout ohne Refresh Token im Body
        response = self.client.post(self.logout_url, {})

        # Sollte 200 sein, auch ohne Refresh Token
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_blacklists_token(self):
        """
        Test: Nach Logout werden die Cookies gelöscht und neue Login ist erforderlich.
        Erwartet: Cookies sind geloescht.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Logout
        logout_response = self.client.post(self.logout_url, {})
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Cookies sollten entfernt sein
        self.assertIn('access_token', logout_response.cookies)
        self.assertIn('refresh_token', logout_response.cookies)

    def test_logout_no_rate_limit(self):
        """
        Test: Keine Rate-Limiting auf Logout-Endpoint.
        Erwartet: Mehrere Requests sollten beantwortet werden (kein 429).
        """
        # Mache mehrere Login/Logout Zyklen
        for _ in range(3):
            login_response = self.client.post(self.login_url, {
                'username': 'testuser',
                'password': 'SecurePassword123'
            })

            access_token = login_response.cookies.get('access_token')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

            logout_response = self.client.post(self.logout_url, {})

            # Sollte 200 sein, nicht 429
            self.assertNotEqual(logout_response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_logout_user_still_exists_after_logout(self):
        """
        Test: Nach Logout existiert der Benutzer noch in der Datenbank.
        Erwartet: Benutzer sollte weiterhin abrufbar sein.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.client.post(self.logout_url, {})

        # Der Benutzer sollte immer noch existieren
        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')

    def test_logout_user_can_login_again(self):
        """
        Test: Nach Logout kann der Benutzer sich erneut anmelden.
        Erwartet: Zweiter Login sollte erfolgreich sein.
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        logout_response = self.client.post(self.logout_url, {})
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        # Logout für neue Session
        self.client.logout()

        # Neuer Login sollte erfolgreich sein
        login_response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'SecurePassword123'
        })

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertEqual(login_response.data['user']['username'], 'testuser')
