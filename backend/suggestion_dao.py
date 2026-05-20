from dao import DAO


class SuggestionDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def list_suggestions(self):
        self.cursor.execute(
            """
            SELECT s.id, s.title, s.user_email, u.name AS user_name, s.recipe_name, s.created_at,
                   s.dish_id, d.name AS dish_name, COUNT(*) AS supports
                   (SELECT COUNT(*) FROM suggestion_support ss WHERE ss.suggestion_id = s.id) AS supports
            FROM suggestion s, users u, dish d, suggestion_support sp
            WHERE u.email = s.user_email AND d.id = s.dish_id AND sp.suggestion_id = s.id
            GROUP BY s.id
            ORDER BY supports DESC, s.created_at DESC
            """
        )
        return self.cursor.fetchall()

    def create_suggestion(
        self, user_email, timestamp, dish_id, title, recipe_name, recipe_data, created_at
    ):
        cur = self.cursor.execute(
            """
            INSERT INTO suggestion (user_email, timestamp, dish_id, title, recipe_name, recipe_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_email, timestamp, dish_id, title, recipe_name, recipe_data, created_at),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_recipe_by_suggestion_id(self, suggestion_id):
        self.cursor.execute(
            """
            SELECT recipe_name, recipe_data
            FROM suggestion
            WHERE id = ?
            """,
            (suggestion_id,),
        )
        return self.cursor.fetchone()

    def suggestion_exists(self, suggestion_id):
        self.cursor.execute("SELECT id FROM suggestion WHERE id = ?", (suggestion_id,))
        return self.cursor.fetchone() is not None

    def has_user_supported(self, suggestion_id, user_email):
        self.cursor.execute(
            """
            SELECT 1 FROM suggestion_support
            WHERE suggestion_id = ? AND user_email = ?
            """,
            (suggestion_id, user_email),
        )
        return self.cursor.fetchone() is not None

    def add_support(self, suggestion_id, user_email, created_at):
        self.cursor.execute(
            """
            INSERT INTO suggestion_support (suggestion_id, user_email, created_at)
            VALUES (?, ?, ?)
            """,
            (suggestion_id, user_email, created_at),
        )
        self.conn.commit()
        return True
