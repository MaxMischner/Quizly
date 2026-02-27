"""
Tests for user registration.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class UserRegistrationTests(TestCase):
    """
    Tests für die POST /api/register/ Endpoint.
    Testet erfolgreiche Registrierung und verschiedene Fehlerszenarien.
    """

    def setUp(self):
        """Initialisiere API Client für Tests."""
        self.client = APIClient()
        self.register_url = reverse('register')

        # Test-Daten
        self.valid_user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'SecurePassword123',
            'confirmed_password': 'SecurePassword123'
        }

    def test_user_registration_success(self):
        """
        Test: Erfolgreiche Benutzerregistrierung mit gültigen Daten.
        Erwartet: 201 Status Code und "User created successfully!" Nachricht.
        """
        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'User created successfully!')
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

    def test_user_created_in_database(self):
        """
        Test: Benutzer wird korrekt in der Datenbank erstellt.
        Überprüft Username, Email und Password-Hashing.
        """
        self.client.post(self.register_url, self.valid_user_data)

        user = CustomUser.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('SecurePassword123'))

    def test_registration_missing_username(self):
        """
        Test: Registrierung ohne Username schlägt fehl.
        Erwartet: 400 Status Code mit Error-Details.
        """
        data = self.valid_user_data.copy()
        del data['username']

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_missing_email(self):
        """
        Test: Registrierung ohne Email schlägt fehl.
        Erwartet: 400 Status Code mit Error-Details.
        """
        data = self.valid_user_data.copy()
        del data['email']

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_missing_password(self):
        """
        Test: Registrierung ohne Password schlägt fehl.
        Erwartet: 400 Status Code mit Error-Details.
        """
        data = self.valid_user_data.copy()
        del data['password']

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_missing_confirmed_password(self):
        """
        Test: Registrierung ohne confirmed_password schlägt fehl.
        Erwartet: 400 Status Code mit Error-Details.
        """
        data = self.valid_user_data.copy()
        del data['confirmed_password']

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirmed_password', response.data)

    def test_registration_password_mismatch(self):
        """
        Test: Passwörter stimmen nicht überein.
        Erwartet: 400 Status Code mit Validierungsfehler.
        """
        data = self.valid_user_data.copy()
        data['confirmed_password'] = 'DifferentPassword123'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_registration_duplicate_email(self):
        """
        Test: Email ist bereits registriert.
        Erwartet: 400 Status Code mit Validierungsfehler.
        """
        # Erstelle ersten Benutzer
        self.client.post(self.register_url, self.valid_user_data)

        # Versuche, einen neuen Benutzer mit gleicher Email zu erstellen
        data = self.valid_user_data.copy()
        data['username'] = 'anotheruser'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_short_password(self):
        """
        Test: Passwort ist kürzer als 8 Zeichen.
        Erwartet: 400 Status Code mit Validierungsfehler.
        """
        data = self.valid_user_data.copy()
        data['password'] = 'Short'
        data['confirmed_password'] = 'Short'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_empty_username(self):
        """
        Test: Username ist leer.
        Erwartet: 400 Status Code mit Error.
        """
        data = self.valid_user_data.copy()
        data['username'] = ''

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_empty_email(self):
        """
        Test: Email ist leer.
        Erwartet: 400 Status Code mit Error.
        """
        data = self.valid_user_data.copy()
        data['email'] = ''

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_invalid_email_format(self):
        """
        Test: Email hat ungültiges Format.
        Erwartet: 400 Status Code mit Error.
        """
        data = self.valid_user_data.copy()
        data['email'] = 'notanemail'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_duplicate_username(self):
        """
        Test: Username ist bereits registriert.
        Erwartet: 400 Status Code mit Validierungsfehler.
        """
        # Erstelle ersten Benutzer
        self.client.post(self.register_url, self.valid_user_data)

        # Versuche, einen neuen Benutzer mit gleichem Username zu erstellen
        data = self.valid_user_data.copy()
        data['email'] = 'different@example.com'

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_registration_response_format(self):
        """
        Test: Response hat das korrekte Format.
        Erwartet: JSON mit 'detail' Feld.
        """
        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertIn('detail', response.data)
        self.assertIsInstance(response.data['detail'], str)

    def test_registration_no_password_in_response(self):
        """
        Test: Password wird nicht in Response zurückgesendet.
        Sicherheit: Passwort sollte niemals in Response sichtbar sein.
        """
        response = self.client.post(self.register_url, self.valid_user_data)

        self.assertNotIn('password', response.data)
        self.assertNotIn('confirmed_password', response.data)

    def test_registration_special_characters_in_password(self):
        """
        Test: Passwort mit Sonderzeichen funktioniert.
        Erwartet: 201 Status Code.
        """
        data = self.valid_user_data.copy()
        password = 'P@$sw0rd!#%'
        data['password'] = password
        data['confirmed_password'] = password

        response = self.client.post(self.register_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(username='testuser')
        self.assertTrue(user.check_password(password))

    def test_registration_case_sensitive_username(self):
        """
        Test: Username mit verschiedenen Cases sind unterschiedlich.
        Erwartet: Beide sollten registriert werden können (falls Django default).
        """
        # Registriere ersten Benutzer
        self.client.post(self.register_url, self.valid_user_data)

        # Versuche, Benutzer mit gleichem Username aber unterschiedliches Case zu registrieren
        data = self.valid_user_data.copy()
        data['username'] = 'TestUser'
        data['email'] = 'testuser2@example.com'

        response = self.client.post(self.register_url, data)

        # Django behandelt usernames standardmäßig als case-sensitive
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_no_authentication_required(self):
        """
        Test: Registrierung erfordert keine Authentifizierung.
        Erwartet: 201 auch ohne Authorization Header.
        """
        response = self.client.post(self.register_url, self.valid_user_data)

        # Sollte erfolgreich sein, ohne Token zu benötigen
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registration_no_rate_limit(self):
        """
        Test: Keine Rate-Limiting auf Register-Endpoint (gemaess Spezifikation).
        Erwartet: Mehrere Anfragen sollten alle 201/400 sein (kein 429).
        """
        responses = []
        for i in range(3):
            data = self.valid_user_data.copy()
            data['username'] = f'user{i}'
            data['email'] = f'user{i}@example.com'
            response = self.client.post(self.register_url, data)
            responses.append(response.status_code)

        # Alle sollten entweder 201 (erfolgreich) oder 400 (invalid) sein,
        # aber nicht 429 (Too Many Requests)
        for status_code in responses:
            self.assertNotEqual(status_code, status.HTTP_429_TOO_MANY_REQUESTS)
