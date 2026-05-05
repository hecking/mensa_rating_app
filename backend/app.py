import base64
import hashlib
import os
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, g, jsonify, request

APP_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def iso_week_key(d):
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def upcoming_week_keys(count=6):
    start = date.today()
    return [iso_week_key(start + timedelta(days=7 * i)) for i in range(count)]


def default_meals_by_day():
    return {
        "Monday": ["Pasta Arrabbiata", "Vegan Bowl", "Chicken Wrap"],
        "Tuesday": ["Potato Soup", "Tofu Stir Fry", "Fish Curry"],
        "Wednesday": ["Lentil Stew", "Veggie Burger", "Beef Chili"],
        "Thursday": ["Pumpkin Risotto", "Falafel Plate", "Turkey Rice"],
        "Friday": ["Spinach Lasagna", "Sushi Bowl", "Pizza Margherita"],
    }


def init_db():
    # Create tables and dummy data


@app.after_request
def cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/api/<path:_path>", methods=["OPTIONS"])
def options_handler(_path):
    return ("", 204)


def login_required(handler):
    @wraps(handler)
    def wrapped(*args, **kwargs):
        user = token_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        return handler(user, *args, **kwargs)

    return wrapped


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400

    # TODO: Implement registration


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    # TODO: Implement login


@app.post("/api/auth/logout")
@login_required
def logout(user):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    
    # TODO: Implement logout


@app.get("/api/weeks")
def list_weeks():
    
    # TODO: Implement list weeks


@app.get("/api/menus/<week_key>")
def get_menu(week_key):
    # TODO: Implement get menu


def weekdays():
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


@app.get("/api/ratings")
def list_ratings():
    # TODO: Implement list ratings


@app.post("/api/ratings")
@login_required
def create_rating(user):
    week_key = str(request.form.get("weekKey", "")).strip()
    day = str(request.form.get("day", "")).strip()
    meal = str(request.form.get("meal", "")).strip()
    score_raw = request.form.get("score")
    comment = str(request.form.get("comment", "")).strip() or None
    photo = request.files.get("photo")

    if not week_key or not day or not meal or not score_raw:
        return jsonify({"error": "weekKey, day, meal and score are required"}), 400
    try:
        score = int(score_raw)
    except ValueError:
        return jsonify({"error": "score must be a number"}), 400
    if score < 1 or score > 5:
        return jsonify({"error": "score must be between 1 and 5"}), 400

    photo_name = None
    photo_data = None
    if photo and photo.filename:
        photo_name = photo.filename
        photo_data = photo.read()

    rating_id = uuid.uuid4().hex
    
    # TODO: Implement create rating


@app.get("/api/ratings/<rating_id>/photo")
def get_rating_photo(rating_id):
    # TODO: Implement get rating photo


@app.get("/api/suggestions")
def list_suggestions():
    # TODO: Implement list suggestions


@app.post("/api/suggestions")
@login_required
def create_suggestion(user):
    title = str(request.form.get("title", "")).strip()
    recipe = request.files.get("recipe")
    if not title or not recipe or not recipe.filename:
        return jsonify({"error": "title and recipe file are required"}), 400

    suggestion_id = uuid.uuid4().hex
    
    # TODO: Implement create suggestion

@app.get("/api/suggestions/<suggestion_id>/recipe")
def get_recipe(suggestion_id):
    
    # TODO: Implement get recipe

@app.post("/api/suggestions/<suggestion_id>/support")
@login_required
def support_suggestion(user, suggestion_id):
    
    # TODO: Implement support suggestion



if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
