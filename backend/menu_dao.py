from dao import DAO


class MenuDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_menu_item(self, week_key, day, dish_id):
        self.cursor.execute(
            """
            INSERT INTO menu_item (week_key, day, dish_id)
            VALUES (?, ?, ?)
            """,
            (week_key, day, dish_id),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_menu_item_by_id(self, week_key, day):
        self.cursor.execute(
            """
            SELECT week_key, day, dish_id
            FROM menu_item
            WHERE week_key = ? AND day = ?
            ORDER BY dish_id
            """,
            (week_key, day),
        )
        return self.cursor.fetchall()

    def get_menu_for_week(self, week_key):
        self.cursor.execute(
            """
            SELECT m.day, d.id AS dish_id, d.name AS dish_name
            FROM menu_item m, dish d
            WHERE d.id = m.dish_id
            AND m.week_key = ?
            ORDER BY m.day, d.name
            """,
            (week_key,),
        )
        return self.cursor.fetchall()

    def create_many_menu_items(self, week_key, day, dish_ids):
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO menu_item (week_key, day, dish_id)
            VALUES (?, ?, ?)
            """,
            [(week_key, day, dish_id) for dish_id in dish_ids],
        )
        self.conn.commit()

    def delete_menu_item(self, week_key, day):
        self.cursor.execute(
            "DELETE FROM menu_item WHERE week_key = ? AND day = ?",
            (week_key, day),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0