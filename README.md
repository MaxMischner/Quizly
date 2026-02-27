# Quizly Backend

Quizly ist ein innovatives Quiz-Generierungs-System, das YouTube-Videos automatisch in interaktive Quizzes umwandelt.

## Features

✅ **YouTube zu Quiz Pipeline**
- Videos automatisch herunterladen
- Audio mit FFMPEG extrahieren
- Transkript mit Whisper AI generieren
- Quiz mit Google Gemini Flash AI erstellen

✅ **User Management**
- Benutzerregistrierung und Anmeldung
- JWT-authentifizierung mit Refresh-Tokens
- HTTP-Only Cookies für sichere Token-Speicherung
- Token-Blacklisting beim Logout

✅ **Quiz Management**
- Quiz erstellen, bearbeiten, löschen
- 10 Fragen mit jeweils 4 Antwortmöglichkeiten
- Quiz-Spielsessions mit Fortschritt-Speicherung
- Auswertung mit Prozentangabe

✅ **Admin Panel**
- Umfassendes Django Admin Interface
- Quizzes und Fragen verwalten
- Benutzer und Token-Blacklist einsehen

---

## Voraussetzungen

- **Python 3.10+**
- **FFMPEG** (global installiert) - Für Audio-Konvertierung
- **Google Gemini API-Key** - Kostenlos von https://ai.google.dev
- Windows/Mac/Linux

### FFMPEG Installation

**Windows (mit winget):**
```powershell
winget install ffmpeg
```

**macOS (mit Homebrew):**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

---

## Installation

### 1. Repository klonen
```bash
git clone https://github.com/YourUsername/Quizly.git
cd Quizly
```

### 2. Virtual Environment erstellen
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Umgebungsvariablen konfigurieren
```bash
# Kopiere .env.example zu .env
cp .env.example .env
```

Bearbeite `.env` und füge deine Gemini API-Key ein:
```
GEMINI_API_KEY=dein-api-key-hier
```

### 5. Datenbank initialisieren
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Server starten
```bash
python manage.py runserver
```

Server läuft unter: `http://localhost:8000`
Admin Panel: `http://localhost:8000/admin`

---

## API Endpoints

### Authentifizierung

**Registrierung**
```
POST /api/users/register/
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123"
}
```

**Login**
```
POST /api/token/
{
    "username": "testuser",
    "password": "SecurePass123"
}
Response:
{
    "access": "eyJ...",
    "refresh": "eyJ..."
}
```

**Logout**
```
POST /api/users/logout/
Authorization: Bearer {access_token}
{
    "refresh": "{refresh_token}"
}
```

### Quizzes

**Quiz erstellen**
```
POST /api/quizzes/
Authorization: Bearer {access_token}
{
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "title": "Quiz Titel",
    "description": "Beschreibung"
}
```

**Alle Quizzes abrufen**
```
GET /api/quizzes/
Authorization: Bearer {access_token}
```

**Quiz-Detail abrufen**
```
GET /api/quizzes/{id}/
Authorization: Bearer {access_token}
```

**Quiz bearbeiten**
```
PUT /api/quizzes/{id}/
PATCH /api/quizzes/{id}/
Authorization: Bearer {access_token}
{
    "title": "Neuer Titel",
    "description": "Neue Beschreibung"
}
```

**Quiz löschen**
```
DELETE /api/quizzes/{id}/
Authorization: Bearer {access_token}
```

**Quiz starten**
```
POST /api/quizzes/{id}/start_quiz/
Authorization: Bearer {access_token}
Response:
{
    "detail": "Quiz gestartet",
    "response_id": 1
}
```

**Heute erstellte Quizzes**
```
GET /api/quizzes/today/
Authorization: Bearer {access_token}
```

**Quizzes der letzten 7 Tage**
```
GET /api/quizzes/last_seven_days/
Authorization: Bearer {access_token}
```

---

## Projektstruktur

```
quizly_backend/
├── users/              # Benutzer & Authentifizierung
│   ├── models.py       # CustomUser, TokenBlacklist
│   ├── views.py        # Register, Login, Logout
│   ├── serializers.py  # UserSerializer, RegisterSerializer
│   ├── urls.py         # Auth Endpoints
│   └── admin.py        # Admin Interface
│
├── quizzes/            # Quiz Management
│   ├── models.py       # Quiz, Question, Answer, QuizResponse, UserAnswer
│   ├── views.py        # QuizViewSet
│   ├── serializers.py  # Quiz Serializer
│   ├── urls.py         # Quiz Endpoints
│   └── admin.py        # Quiz Admin Interface
│
├── core/               # Core Utilities & Services
│   ├── services.py     # YouTubeService, TranscriptionService, QuizGeneratorService
│   └── admin.py        # Core Admin
│
├── quizly_backend/     # Django Projekt Settings
│   ├── settings.py     # Django Settings
│   ├── urls.py         # URL Router
│   └── wsgi.py         # WSGI App
│
├── manage.py           # Django Management
├── requirements.txt    # Python Dependencies
├── .env.example        # Umgebungsvariablen Template
└── README.md           # Diese Datei
```

---

## Clean Code Standards

Dieses Projekt befolgt die Definition of Done (DoD):

### Code Quality
- ✅ Funktionen maximal 14 Zeilen
- ✅ Jede Funktion hat eine Aufgabe
- ✅ snake_case für Funktionsnamen
- ✅ Sprechende Variablennamen
- ✅ Keine toten Variablen
- ✅ Kein auskommentierter Code
- ✅ PEP-8 compliant

### Dokumentation
- ✅ Docstrings für alle Module/Funktionen
- ✅ Type Hints wo nötig
- ✅ README.md aktuell und aussagekräftig

### Django Best Practices
- ✅ Views nur in views.py
- ✅ Hilfsfunktionen in utils.py/functions.py
- ✅ Modell-Admin-Panel gepflegt
- ✅ REST-API für Frontend

---

## Technische Anforderungen

### Backend
- Django 6.0.2
- Django REST Framework 3.16.1
- JWT-Authentifizierung mit Refresh-Tokens
- CORS für Frontend-Integration

### AI/ML
- **Whisper** (OpenAI) - Audio-Transkription
- **Gemini 1.5 Flash** (Google) - Quiz-Generierung
- **yt-dlp** - YouTube Video Download
- **FFMPEG** - Audio-Format-Konvertierung

### Token Management
- Access Token: 15 Minuten Gültigkeit
- Refresh Token: 7 Tage Gültigkeit
- HTTP-Only Cookies für sichere Token-Speicherung
- Token Blacklisting nach Logout

---

## Entwicklung

### Tests ausführen
```bash
pytest
pytest --cov=.
```

### Code formatieren
```bash
black .
flake8 .
```

### Migrationen erstellen
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Umgebungsvariablen

```env
# Django
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key

# APIs
GEMINI_API_KEY=your-gemini-api-key

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Sicherheit

⚠️ **PRODUCTION:**
- `DEBUG=False` setzen
- `SECRET_KEY` mit sicherem Wert ändern
- `ALLOWED_HOSTS` konfigurieren
- HTTPS verwenden
- Datenbankpasswörter schützen
- API-Keys in Secret Management speichern

---

## Support & Kontakt

Bei Fragen oder Problemen bitte ein Issue auf GitHub erstellen.

---

## Lizenz

MIT License - siehe LICENSE.md

---

## Contributors

- Maxim Developer
- Developer Akademie

Die Erstellung dieses Projekts folgt der Definition of Done der Developer Akademie.
