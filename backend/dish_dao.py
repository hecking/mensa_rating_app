from dao import DAO


class DishDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def get_or_create_dish(self, name, description=None):
        self.cursor.execute("SELECT id, name, description FROM dish WHERE name = ?", (name,))
        row = self.cursor.fetchone()
        if row:
            return row
        self.cursor.execute(
            "INSERT INTO dish (name, description) VALUES (?, ?)",
            (name, description),
        )
        self.conn.commit()
        new_id = self.cursor.lastrowid
        self.cursor.execute("SELECT id, name, description FROM dish WHERE id = ?", (new_id,))
        return self.cursor.fetchone()

    def get_dish_by_id(self, dish_id):
        self.cursor.execute("SELECT id, name, description FROM dish WHERE id = ?", (dish_id,))
        return self.cursor.fetchone()

    def list_dishes(self):
        self.cursor.execute("SELECT id, name, description FROM dish ORDER BY name ASC")
        return self.cursor.fetchall()
