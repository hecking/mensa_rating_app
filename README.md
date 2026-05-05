# Mensa Rating Frontend

Lightweight web frontend for student restaurant menus, ratings, and meal suggestions.

## Run

Option 1 (simplest):

1. Open `public/index.html` in your browser.

Option 2 (recommended for development):

1. In this project folder run:
   - `python -m http.server 8000`
2. Open [http://localhost:8000/public](http://localhost:8000/public)

## Backend (Python + SQLite)

1. Install dependency:
   - `pip install -r requirements.txt`
2. Start backend:
   - `python backend/app.py`
3. Backend runs on:
   - `http://127.0.0.1:5000`

The SQLite database file is auto-created at `backend/mensa.db`.

## Features

- Weekly menu plans (Monday to Friday), with upcoming weeks pre-generated
- New menu plan each week (week selector)
- Student account registration and login
- Logged in students can rate meals (1-5 stars) with optional comment + food photo upload
- Logged in students can submit meal suggestions by uploading recipe files
- Other logged in students can support suggestions using a thumbs-up button
- All data stored in browser localStorage (no backend needed for first prototype)

## Important note

This is a local prototype, so authentication is not secure (passwords are stored in localStorage).
Use this as a frontend concept/demo. For production, connect to a real backend and secure auth.

For the backend scaffold, passwords are hashed with SHA-256, but this is still not production-ready.

## API endpoints for frontend integration

- `GET /api/health`
- `POST /api/auth/register` (JSON: `name`, `email`, `password`)
- `POST /api/auth/login` (JSON: `email`, `password`) -> returns bearer token
- `POST /api/auth/logout` (Authorization: `Bearer <token>`)
- `GET /api/weeks`
- `GET /api/menus/<weekKey>`
- `GET /api/ratings?weekKey=<optional>`
- `POST /api/ratings` (multipart form: `weekKey`, `day`, `meal`, `score`, `comment?`, `photo?`)
- `GET /api/ratings/<ratingId>/photo`
- `GET /api/suggestions`
- `POST /api/suggestions` (multipart form: `title`, `recipe`)
- `GET /api/suggestions/<suggestionId>/recipe`
- `POST /api/suggestions/<suggestionId>/support` (Authorization required)
