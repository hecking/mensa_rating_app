import base64
import hashlib
import os
import uuid
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, request

from dao import DAO
from dish_dao import DishDAO
from menu_dao import MenuDAO
from rating_dao import RatingDAO
from suggestion_dao import SuggestionDAO
from user_dao import UserDAO

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "mensa.db")

app = Flask(__name__)
TOKENS = {}


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
    dao = DAO(DB_PATH)
    dao.init_db()
    dao.close()


def token_user():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    return TOKENS.get(token)


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

    created_at = datetime.utcnow().isoformat()
    user_dao = UserDAO(DB_PATH)
    try:
        created = user_dao.create_user_with_name(
            name, email, hash_password(password), created_at
        )
    finally:
        user_dao.close()
    if not created:
        return jsonify({"error": "Email already exists"}), 409
    return jsonify({"ok": True, "email": email}), 201


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user_dao = UserDAO(DB_PATH)
    try:
        user = user_dao.get_user_by_email_and_password(email, hash_password(password))
    finally:
        user_dao.close()
    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    token = uuid.uuid4().hex
    TOKENS[token] = {"email": user["email"], "name": user["name"]}
    return jsonify({"token": token, "user": {"email": user["email"], "name": user["name"]}})


@app.post("/api/auth/logout")
@login_required
def logout(user):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip()
    
    TOKENS.pop(token, None)
    return jsonify({"ok": True})


@app.get("/api/weeks")
def list_weeks():
    return jsonify({"weeks": upcoming_week_keys()})


@app.get("/api/menus/<week_key>")
def get_menu(week_key):
    dish_dao = DishDAO(DB_PATH)
    menu_dao = MenuDAO(DB_PATH)
    try:
        # Seed missing menus for the week with default dishes.
        if not menu_dao.get_menu_for_week(week_key):
            for day, dish_names in default_meals_by_day().items():
                dish_ids = []
                for dish_name in dish_names:
                    dish = dish_dao.get_or_create_dish(dish_name)
                    dish_ids.append(dish["id"])
                menu_dao.create_many_menu_items(week_key, day, dish_ids)
        rows = menu_dao.get_menu_for_week(week_key)
    finally:
        dish_dao.close()
        menu_dao.close()
    menu = {day: [] for day in weekdays()}
    for row in rows:
        menu[row["day"]].append(row["dish_name"])
    if not rows:
        menu = default_meals_by_day()
    return jsonify({"weekKey": week_key, "days": menu})


def weekdays():
    return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


@app.get("/api/ratings")
def list_ratings():
    week_key = str(request.args.get("weekKey", "")).strip()
    rating_dao = RatingDAO(DB_PATH)
    try:
        rows = rating_dao.list_ratings(week_key if week_key else None)
    finally:
        rating_dao.close()
    return jsonify(
        {
            "ratings": [
                {
                    "id": row["rating_id"],
                    "userEmail": row["user_email"],
                    "userName": row["user_name"] or row["user_email"],
                    "weekKey": row["week_key"],
                    "day": row["day"],
                    "meal": row["meal"],
                    "score": row["score"],
                    "comment": row["comment"],
                    "hasPhoto": bool(row["photo_name"]),
                    "createdAt": row["created_at"],
                    "dishId": row["dish_id"],
                    "dishName": row["dish_name"] or row["meal"],
                }
                for row in rows
            ]
        }
    )


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
    now = datetime.utcnow().isoformat()
    dish_dao = DishDAO(DB_PATH)
    rating_dao = RatingDAO(DB_PATH)
    try:
        dish = dish_dao.get_or_create_dish(meal)
        rating_dao.create_rating_entry(
            user["email"],
            now,
            dish["id"],
            score,
            comment,
            now,
            week_key,
            day,
            meal,
            photo_name,
            photo_data,
            rating_id,
        )
    finally:
        dish_dao.close()
        rating_dao.close()
    return jsonify({"id": rating_id}), 201


@app.get("/api/ratings/<rating_id>/photo")
def get_rating_photo(rating_id):
    rating_dao = RatingDAO(DB_PATH)
    try:
        row = rating_dao.get_rating_photo_by_rating_id(rating_id)
    finally:
        rating_dao.close()
    if not row or not row["photo_data"]:
        return jsonify({"error": "Photo not found"}), 404
    return jsonify(
        {
            "fileName": row["photo_name"],
            "dataBase64": base64.b64encode(row["photo_data"]).decode("ascii"),
        }
    )


@app.get("/api/suggestions")
def list_suggestions():
    suggestion_dao = SuggestionDAO(DB_PATH)
    try:
        rows = suggestion_dao.list_suggestions()
    finally:
        suggestion_dao.close()
    return jsonify(
        {
            "suggestions": [
                {
                    "id": str(row["id"]),
                    "title": row["title"],
                    "createdByEmail": row["user_email"],
                    "createdByName": row["user_name"] or row["user_email"],
                    "recipeName": row["recipe_name"],
                    "dishId": row["dish_id"],
                    "dishName": row["dish_name"] or row["title"],
                    "supportCount": row["supports"],
                    "createdAt": row["created_at"],
                }
                for row in rows
            ]
        }
    )


@app.post("/api/suggestions")
@login_required
def create_suggestion(user):
    title = str(request.form.get("title", "")).strip()
    recipe = request.files.get("recipe")
    if not title or not recipe or not recipe.filename:
        return jsonify({"error": "title and recipe file are required"}), 400

    now = datetime.utcnow().isoformat()
    recipe_data = recipe.read()
    recipe_name = recipe.filename
    dish_dao = DishDAO(DB_PATH)
    suggestion_dao = SuggestionDAO(DB_PATH)
    try:
        dish = dish_dao.get_or_create_dish(title)
        suggestion_id = suggestion_dao.create_suggestion(
            user["email"], now, dish["id"], title, recipe_name, recipe_data, now
        )
        suggestion_dao.add_support(suggestion_id, user["email"], now)
    finally:
        dish_dao.close()
        suggestion_dao.close()
    return jsonify({"id": suggestion_id}), 201

@app.get("/api/suggestions/<suggestion_id>/recipe")
def get_recipe(suggestion_id):
    suggestion_dao = SuggestionDAO(DB_PATH)
    try:
        row = suggestion_dao.get_recipe_by_suggestion_id(suggestion_id)
    finally:
        suggestion_dao.close()
    if not row or not row["recipe_data"]:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(
        {
            "fileName": row["recipe_name"],
            "dataBase64": base64.b64encode(row["recipe_data"]).decode("ascii"),
        }
    )

@app.post("/api/suggestions/<suggestion_id>/support")
@login_required
def support_suggestion(user, suggestion_id):
    now = datetime.utcnow().isoformat()
    suggestion_dao = SuggestionDAO(DB_PATH)
    try:
        if not suggestion_dao.suggestion_exists(suggestion_id):
            return jsonify({"error": "Suggestion not found"}), 404
        if suggestion_dao.has_user_supported(suggestion_id, user["email"]):
            return jsonify({"ok": True, "alreadySupported": True})
        suggestion_dao.add_support(suggestion_id, user["email"], now)
    finally:
        suggestion_dao.close()
    return jsonify({"ok": True, "alreadySupported": False})


@app.get("/api/dishes")
def list_dishes():
    dish_dao = DishDAO(DB_PATH)
    try:
        rows = dish_dao.list_dishes()
    finally:
        dish_dao.close()
    return jsonify(
        {
            "dishes": [
                {"id": row["id"], "name": row["name"], "description": row["description"]}
                for row in rows
            ]
        }
    )



if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
