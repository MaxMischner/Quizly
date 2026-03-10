# Quizly

## Project Overview
Quizly is built as a Django REST Framework backend that turns YouTube videos into quizzes.
This repository now also contains a static frontend (HTML/CSS/JS assets) that consumes the API.

## Requirements
- Python 3.10+
- `pip`
- `venv`
- FFmpeg (required for audio extraction from YouTube)

## Local Backend Setup
```bash
git clone https://github.com/MaxMischner/Quizly.git
cd Quizly

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

python manage.py migrate
python manage.py runserver
```

Windows activation equivalent:
```powershell
venv\Scripts\Activate.ps1
```

## Environment Variables
Configure your `.env` file with at least:

```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
GEMINI_API_KEY=your-gemini-api-key-here
```

## Running the Backend
```bash
python manage.py migrate
python manage.py runserver
```

Optional checks:
```bash
python manage.py check
python manage.py test
```

## API Overview
Base URL (local): `http://127.0.0.1:8000`

Core endpoints:
- `POST /api/register/`
- `POST /api/login/`
- `POST /api/logout/`
- `POST /api/token/refresh/`
- `GET /api/profile/`
- `GET|POST /api/quizzes/`
- `GET|PATCH|DELETE /api/quizzes/{id}/`
- `POST /api/quizzes/{id}/start_quiz/`
- `POST /api/quizzes/{id}/submit_answer/`
- `POST /api/quizzes/{id}/complete_quiz/`
- `GET /api/quizzes/today/`
- `GET /api/quizzes/last_seven_days/`

## Frontend
Frontend assets and pages are included in:
- `index.html`
- `pages/`
- `shared/`
- `assets/`

To run the frontend locally, serve the repo with a local web server (for example VS Code Live Server) while the backend API is running.

## Optional Docker Deployment
Docker is optional and not required for local backend development.
If you want to use Docker, keep and use these files when available:
- `Dockerfile`
- `compose.yaml`

Typical optional Docker flow:
```bash
docker compose up --build
```
