from dao import DAO


class RatingDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_rating(self, user_email, timestamp, dish_id, score, comment, created_at):
        self.cursor.execute(
            """
            INSERT INTO rating (user_email, timestamp, dish_id, score, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_email, timestamp, dish_id, score, comment, created_at),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_rating_by_id(self, user_email, timestamp):
        self.cursor.execute(
            """
            SELECT user_email, timestamp, dish_id, score, comment, created_at
            FROM rating
            WHERE user_email = ? AND timestamp = ?
            """,
            (user_email, timestamp),
        )
        return self.cursor.fetchone()

    def delete_rating(self, user_email, timestamp):
        self.cursor.execute(
            "DELETE FROM rating WHERE user_email = ? AND timestamp = ?",
            (user_email, timestamp),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_rating(self, user_email, timestamp, dish_id, score, comment, created_at):
        self.cursor.execute(
            """
            UPDATE rating
            SET dish_id = ?, score = ?, comment = ?, created_at = ?
            WHERE user_email = ? AND timestamp = ?
            """,
            (dish_id, score, comment, created_at, user_email, timestamp),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_ratings_for_dish(self, dish_id):
        self.cursor.execute(
            """
            SELECT user_email, timestamp, dish_id, score, comment, created_at
            FROM rating
            WHERE dish_id = ?
            ORDER BY created_at DESC
            """,
            (dish_id,),
        )
        return self.cursor.fetchall()

    def get_ratings_for_user(self, user_email):
        self.cursor.execute(
            """
            SELECT user_email, timestamp, dish_id, score, comment, created_at
            FROM rating
            WHERE user_email = ?
            ORDER BY created_at DESC
            """,
            (user_email,),
        )
        return self.cursor.fetchall()

    def get_ratings_for_week(self, week_key):
        self.cursor.execute(
            """
            SELECT user_email, timestamp, dish_id, score, comment, created_at
            FROM rating
            WHERE week_key = ?
            ORDER BY created_at DESC
            """,
            (week_key,),
        )
        return self.cursor.fetchall()

    def get_ratings_for_day(self, day):
        self.cursor.execute(
            """
            SELECT user_email, timestamp, dish_id, score, comment, created_at
            FROM rating
            WHERE day = ?
            ORDER BY created_at DESC
            """,
            (day,),
        )
        return self.cursor.fetchall()

    def create_rating_entry(
        self,
        user_email,
        timestamp,
        dish_id,
        score,
        comment,
        created_at,
        week_key,
        day,
        meal,
        photo_name,
        photo_data,
        rating_id,
    ):
        self.cursor.execute(
            """
            INSERT INTO rating (
                user_email, timestamp, dish_id, score, comment, created_at,
                week_key, day, meal, photo_name, photo_data, rating_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_email,
                timestamp,
                dish_id,
                score,
                comment,
                created_at,
                week_key,
                day,
                meal,
                photo_name,
                photo_data,
                rating_id,
            ),
        )
        self.conn.commit()
        return rating_id

    def list_ratings(self, week_key=None):
        query = """
            SELECT r.rating_id, r.user_email, u.name AS user_name, r.week_key, r.day, r.meal,
                   r.score, r.comment, r.photo_name, r.created_at, r.dish_id, d.name AS dish_name
            FROM rating r, users u, dish d
            WHERE d.id = r.dish_id AND u.email = r.user_email
        """
        params = ()
        if week_key:
            query += " WHERE r.week_key = ?"
            params = (week_key,)
        query += " ORDER BY r.created_at DESC"
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_rating_photo_by_rating_id(self, rating_id):
        self.cursor.execute(
            """
            SELECT photo_name, photo_data
            FROM rating
            WHERE rating_id = ?
            """,
            (rating_id,),
        )
        return self.cursor.fetchone()