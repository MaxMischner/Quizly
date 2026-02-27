# Quizly Backend

Quizly ist ein innovatives Quiz-Generierungs-System, das YouTube-Videos automatisch in interaktive Quizzes umwandelt.

> ⚠️ **IMPORTANT**: Der Multi-Terminal-Setup wird benötigt. Siehe Punkt 6 "Server starten".

## Features

✅ **YouTube zu Quiz Pipeline**
- Videos automatisch herunterladen
- Audio mit FFMPEG extrahieren
- Transkript mit Whisper AI generieren
- Quiz mit Google Gemini Flash AI erstellen

✅ **User Management**
- Benutzerregistrierung und Anmeldung
- JWT-Authentifizierung mit Refresh-Tokens
- **HTTP-Only Cookies** für sichere Token-Speicherung (Browser kann tokens nicht via JS auslesen)
- Token-Blacklisting beim Logout
- Support für Cookie-basierte Authentifizierung

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

### 6. Server starten (3 Terminals notwendig!)

⚠️ **WICHTIG**: Verwende **127.0.0.1 statt localhost** für die Cookie-Authentifizierung!

**Terminal 1 - Django Backend:**
```bash
python manage.py runserver 127.0.0.1:8000
```
Backend läuft unter: `http://127.0.0.1:8000`
Admin Panel: `http://127.0.0.1:8000/admin`

**Terminal 2 - Frontend HTTP-Server:**
```bash
python -m http.server 5173 --bind 127.0.0.1
```
Frontend läuft unter: `http://127.0.0.1:5173`

**Terminal 3 - Logging/Monitoring (Optional):**
Weiteres Terminal für Testing oder Monitoring verfügbar.

✅ Beide Server müssen auf `127.0.0.1` laufen für die HTTP-Only-Cookies zu funktionieren!

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
Quizly/
├── users/              # Benutzer & Authentifizierung
│   ├── models.py       # CustomUser, TokenBlacklist
│   ├── views.py        # RegisterView, LoginView, LogoutView, TokenRefreshView
│   ├── serializers.py  # UserSerializer, RegisterSerializer, LoginSerializer
│   ├── urls.py         # Auth Endpoints
│   ├── authentication.py # CookieJWTAuthentication (HTTP-Only Cookie Support)
│   ├── admin.py        # CustomUserAdmin, TokenBlacklistAdmin
│   └── tests/          # User Tests (Registration, Login, Logout, Token Refresh)
│
├── quizzes/            # Quiz Management
│   ├── models.py       # Quiz, Question, Answer, QuizResponse, UserAnswer
│   ├── views.py        # QuizViewSet mit Actions (create, start_quiz, submit_answer, complete_quiz, today, last_seven_days)
│   ├── serializers.py  # QuizSerializer, QuestionSerializer, QuizResponseSerializer, etc.
│   ├── urls.py         # Quiz REST Endpoints
│   ├── admin.py        # QuizAdmin, QuestionAdmin, AnswerAdmin (mit InlineAdmin)
│   └── tests/          # Quiz Tests (Create, List, Detail, Actions, Filters)
│
├── youtube_service/    # YouTube Download Service
│   ├── services.py     # YouTubeService (yt-dlp Integration)
│   └── apps.py
│
├── transcription_service/  # Audio Transkription Service
│   ├── services.py     # TranscriptionService (Whisper AI Integration)
│   └── apps.py
│
├── quiz_generator_service/  # Quiz Generierung mit AI
│   ├── services.py     # QuizGeneratorService (Google Gemini Flash Integration)
│   └── apps.py
│
├── pipeline_service/   # Orchestrierung aller Services
│   ├── services.py     # PipelineService (YouTube → Transkript → Quiz)
│   └── apps.py
│
├── core/               # Django Projekt Settings
│   ├── settings.py     # Django Settings (INSTALLED_APPS, MIDDLEWARE, etc.)
│   ├── urls.py         # Root URL Router
│   ├── asgi.py         # ASGI App
│   └── wsgi.py         # WSGI App
│
├── manage.py           # Django Management CLI
├── requirements.txt    # Python Dependencies (Django, DRF, google-genai, whisper, yt-dlp)
├── .env.example        # Umgebungsvariablen Template (GEMINI_API_KEY)
├── .gitignore          # Git Ignore
├── db.sqlite3          # SQLite Datenbank (Development)
└── README.md           # Diese Datei
```

### Service Architecture
```
User Interface (Frontend)
        ↓
REST API (Django)
        ↓
QuizViewSet (views.py)
        ↓
PipelineService
    ├── YouTubeService (yt-dlp)  → Download
    ├── TranscriptionService (Whisper) → Transkript
    └── QuizGeneratorService (Gemini) → Quiz JSON
        ↓
Quiz Model (Database)
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
- **Whisper** (OpenAI) - Audio-Transkription mit lokalem Modell (base, small, medium, large)
- **Gemini 2.0 Flash** (Google) - Quiz-Generierung via google-genai SDK
  - SDK: `google-genai==0.4.1+` (aktuell, nicht google-generativeai - deprecated!)
  - API-Key: Kostenlos von https://ai.google.dev/gemini-api/docs/api-key
  - Free Tier: 10 Anfragen/Minute, 15000 Anfragen/Tag
- **yt-dlp** - YouTube Video Download & Audio-Extraktion
- **FFMPEG** - Audio-Format-Konvertierung (siehe Voraussetzungen)

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

### Umgebungsvariablen

Vor dem Start müssen folgende Environment-Variablen in `.env` konfiguriert werden:

```env
# Django
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key

# Google Gemini API (kostenlos)
# Generiere einen Key unter: https://ai.google.dev/gemini-api/docs/api-key
GEMINI_API_KEY=your-gemini-api-key
# Der Client lädt diesen Key automatisch bei Verwendung von: from google import genai

# Database
DATABASE_URL=sqlite:///db.sqlite3

# CORS - Frontend URLs (WICHTIG für Cookie-Authentifizierung!)
ALLOWED_HOSTS=127.0.0.1,localhost
# Verwende 127.0.0.1 nicht localhost, damit HTTP-Only-Cookies funktionieren!
```

**Wichtige Hinweise:**
- **GEMINI_API_KEY** ist optional für lokale Entwicklung ohne Quiz-Generierung
- **Cookies funktionieren nur mit 127.0.0.1**, nicht mit localhost (SameSite Policy)

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
