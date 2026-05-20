import sqlite3

from dao import DAO

class UserDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_user(self, email, password_hash, created_at):
        # TODO

    def get_user_by_email_and_password(self, email, password):
        # TODO

    def delete_user(self, email):
        # TODO

    def update_user(self, email, password_hash, created_at):
        # TODO