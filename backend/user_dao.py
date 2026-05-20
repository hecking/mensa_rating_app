import sqlite3

from dao import DAO


class UserDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_user(self, email, password_hash, created_at):
        try:
            self.cursor.execute(
                """
                INSERT INTO users (email, password_hash, created_at)
                VALUES (?, ?, ?)
                """,
                (email, password_hash, created_at),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def create_user_with_name(self, name, email, password_hash, created_at):
        try:
            self.cursor.execute(
                """
                INSERT INTO users (email, password_hash, created_at, name)
                VALUES (?, ?, ?, ?)
                """,
                (email, password_hash, created_at, name),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_user_by_email(self, email):
        self.cursor.execute(
            """
            SELECT email, name, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
        return self.cursor.fetchone()

    def get_user_by_email_and_password(self, email, password):
        self.cursor.execute(
            """
            SELECT email, password_hash, created_at, name
            FROM users
            WHERE email = ? AND password_hash = ?
            """,
            (email, password),
        )
        return self.cursor.fetchone()

    def delete_user(self, email):
        self.cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_user(self, email, password_hash, created_at):
        self.cursor.execute(
            """
            UPDATE users
            SET password_hash = ?, created_at = ?
            WHERE email = ?
            """,
            (password_hash, created_at, email),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0