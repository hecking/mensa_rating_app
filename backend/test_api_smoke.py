import io
import os
import tempfile
import unittest

import app as backend_app


class ApiSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmpdir.name, "test.db")
        backend_app.DB_PATH = self.db_path
        backend_app.TOKENS.clear()
        backend_app.init_db()
        self.client = backend_app.app.test_client()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _register_and_login(self):
        r = self.client.post(
            "/api/auth/register",
            json={"name": "Test User", "email": "test@example.com", "password": "secret"},
        )
        self.assertEqual(r.status_code, 201)
        r = self.client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "secret"},
        )
        self.assertEqual(r.status_code, 200)
        token = r.get_json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_menu_seed_and_dish_endpoint(self):
        week_key = backend_app.upcoming_week_keys(1)[0]
        r = self.client.get(f"/api/menus/{week_key}")
        self.assertEqual(r.status_code, 200)
        payload = r.get_json()
        self.assertIn("Monday", payload["days"])
        self.assertGreater(len(payload["days"]["Monday"]), 0)

        r = self.client.get("/api/dishes")
        self.assertEqual(r.status_code, 200)
        self.assertGreater(len(r.get_json()["dishes"]), 0)

    def test_rating_flow(self):
        headers = self._register_and_login()
        week_key = backend_app.upcoming_week_keys(1)[0]
        self.client.get(f"/api/menus/{week_key}")
        data = {
            "weekKey": week_key,
            "day": "Monday",
            "meal": "Pasta Arrabbiata",
            "score": "5",
            "comment": "Great",
            "photo": (io.BytesIO(b"img"), "food.png"),
        }
        r = self.client.post(
            "/api/ratings",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(r.status_code, 201)
        rating_id = r.get_json()["id"]

        r = self.client.get("/api/ratings")
        self.assertEqual(r.status_code, 200)
        ratings = r.get_json()["ratings"]
        self.assertGreater(len(ratings), 0)
        self.assertIn("dishId", ratings[0])

        r = self.client.get(f"/api/ratings/{rating_id}/photo")
        self.assertEqual(r.status_code, 200)
        self.assertIn("dataBase64", r.get_json())

    def test_suggestion_flow(self):
        headers = self._register_and_login()
        data = {
            "title": "New Veggie Dish",
            "recipe": (io.BytesIO(b"recipe"), "recipe.txt"),
        }
        r = self.client.post(
            "/api/suggestions",
            data=data,
            headers=headers,
            content_type="multipart/form-data",
        )
        self.assertEqual(r.status_code, 201)
        suggestion_id = r.get_json()["id"]

        r = self.client.get("/api/suggestions")
        self.assertEqual(r.status_code, 200)
        suggestions = r.get_json()["suggestions"]
        self.assertGreater(len(suggestions), 0)
        self.assertIn("dishId", suggestions[0])

        r = self.client.post(f"/api/suggestions/{suggestion_id}/support", headers=headers)
        self.assertEqual(r.status_code, 200)
        self.assertIn("alreadySupported", r.get_json())


if __name__ == "__main__":
    unittest.main()
