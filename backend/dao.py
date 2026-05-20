import sqlite3

class DAO:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, query, params=None):
        if params:
            return self.cursor.execute(query, params)
        else:

    def init_db(self):
        '''
        Creates the following database tables:
        - users(email PRIMARY KEY, password_hash, created_at)
        - dish(id PRIMARY KEY, name, description)
        - menu_item(week_key PRIMARY KEY, day PRIMARY KEY, dish_id REFERENCES dish(id) PRIMARY KEY)
        - rating(user_email REFERENCES users(email) PRIMARY KEY, timestamp PRIMARY KEY, dish_id REFERENCES dish(id), score, comment, created_at)
        - suggestion(id PRIMARY_KEY, user_email REFERENCES users(email), timestamp, dish_id REFERENCES dish(id))
        - suggestion_support(suggestion_id REFERENCES suggestion(id) PRIMARY_KEY, user_email REFERENCES users(email) PRIMARY_KEY, created_at)
        '''

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email PRIMARY KEY,
                password_hash,
                created_at
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS dish (
                id PRIMARY KEY,
                name,
                description
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                week_key PRIMARY KEY,
                day PRIMARY KEY,
                dish_id REFERENCES dish(id) PRIMARY KEY
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rating (
                user_email REFERENCES users(email) PRIMARY KEY,
                timestamp PRIMARY KEY,
                dish_id REFERENCES dish(id),
                score,
                comment,
                created_at
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion (
                id PRIMARY KEY,
                user_email REFERENCES users(email),
                timestamp,
                dish_id REFERENCES dish(id)
            )
        """)
        suggestion_support(suggestion_id PRIMARY_KEY, user_email REFERENCES users(email) PRIMARY_KEY, created_at)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestion_support (
                suggestion_id REFERENCES suggestion(id) PRIMARY KEY AUTOINCREMENT,
                user_email REFERENCES users(email) PRIMARY KEY,
                created_at  
            )
        """)    
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_item (
                week_key PRIMARY KEY,
                day PRIMARY KEY,
                dish_id REFERENCES dish(id) PRIMARY KEY
            )
        """)
        self.conn.commit()