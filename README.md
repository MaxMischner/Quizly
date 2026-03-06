# Quizly Backend API

## Project Overview
Quizly is a Django REST Framework backend that turns YouTube videos into quizzes.
It provides authentication endpoints, quiz CRUD endpoints, and quiz play endpoints.

This repository is backend-only and can be run locally without Docker.

## Requirements
- Python 3.10+
- `pip`
- `venv`
- FFmpeg (required for audio extraction from YouTube)

## Local Development Setup
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
Configure your `.env` file with at least the following values:

```env
DEBUG=True
SECRET_KEY=change-me
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
GEMINI_API_KEY=your-gemini-api-key-here
```

Notes:
- `ALLOWED_HOSTS` accepts comma-separated values.
- `CORS_ALLOWED_ORIGINS` accepts comma-separated origins.

## Running the Server
Run database migrations and start the API server:

```bash
python manage.py migrate
python manage.py runserver
```

Optional verification commands:

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

## Optional: Docker Deployment
Docker is optional and not required for local backend development.

If you want to use Docker, keep and use these files when available:
- `Dockerfile`
- `compose.yaml`

Typical optional Docker flow:
```bash
docker compose up --build
```
