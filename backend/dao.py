import sqlite3

class DAO:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, query, params=None):
        if params:
            return self.cursor.execute(query, params)
        else:
            return self.cursor.execute(query)

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL DEFAULT ''
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rating (
                user_email TEXT NOT NULL REFERENCES users(email),
                timestamp TEXT NOT NULL,
                dish_id INTEGER NOT NULL REFERENCES dish(id),
                score INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL,
                week_key TEXT NOT NULL DEFAULT '',
                day TEXT NOT NULL DEFAULT '',
                meal TEXT NOT NULL DEFAULT '',
                photo_name TEXT,
                photo_data BLOB,
                rating_id TEXT NOT NULL DEFAULT '',
                PRIMARY KEY (user_email, timestamp)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL REFERENCES users(email),
                timestamp TEXT NOT NULL,
                dish_id INTEGER NOT NULL REFERENCES dish(id),
                title TEXT NOT NULL DEFAULT '',
                recipe_name TEXT,
                recipe_data BLOB,
                created_at TEXT NOT NULL DEFAULT ''
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion_support (
                suggestion_id INTEGER NOT NULL REFERENCES suggestion(id),
                user_email TEXT NOT NULL REFERENCES users(email),
                created_at TEXT NOT NULL,
                PRIMARY KEY (suggestion_id, user_email)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                week_key TEXT NOT NULL,
                day TEXT NOT NULL,
                dish_id INTEGER NOT NULL REFERENCES dish(id),
                PRIMARY KEY (week_key, day, dish_id)
            )
        """)
        self._add_column_if_missing("users", "name", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("rating", "week_key", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("rating", "day", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("rating", "meal", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("rating", "photo_name", "TEXT")
        self._add_column_if_missing("rating", "photo_data", "BLOB")
        self._add_column_if_missing("rating", "rating_id", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("suggestion", "title", "TEXT NOT NULL DEFAULT ''")
        self._add_column_if_missing("suggestion", "recipe_name", "TEXT")
        self._add_column_if_missing("suggestion", "recipe_data", "BLOB")
        self._add_column_if_missing("suggestion", "created_at", "TEXT NOT NULL DEFAULT ''")
        self._migrate_menu_item_table()
        self.conn.commit()

    def _add_column_if_missing(self, table_name, column_name, column_def):
        cols = self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
        existing = {col[1] for col in cols}
        if column_name not in existing:
            self.cursor.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
            )

    def _migrate_menu_item_table(self):
        cols = self.cursor.execute("PRAGMA table_info(menu_item)").fetchall()
        dish_col = next((col for col in cols if col["name"] == "dish_id"), None)
        if not dish_col or "INT" in str(dish_col["type"]).upper():
            return

        self.cursor.execute("ALTER TABLE menu_item RENAME TO menu_item_old")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS menu_item (
                week_key TEXT NOT NULL,
                day TEXT NOT NULL,
                dish_id INTEGER NOT NULL REFERENCES dish(id),
                PRIMARY KEY (week_key, day, dish_id)
            )
            """
        )
        old_rows = self.cursor.execute(
            "SELECT week_key, day, dish_id FROM menu_item_old"
        ).fetchall()
        for row in old_rows:
            raw_id = row["dish_id"]
            if isinstance(raw_id, int) or (isinstance(raw_id, str) and raw_id.isdigit()):
                dish_id = int(raw_id)
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO menu_item (week_key, day, dish_id)
                    VALUES (?, ?, ?)
                    """,
                    (row["week_key"], row["day"], dish_id),
                )
        self.cursor.execute("DROP TABLE menu_item_old")