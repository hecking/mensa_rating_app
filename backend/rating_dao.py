from dao import DAO

class RatingDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_rating(self, user_email, timestamp, dish_id, score, comment, created_at):
        # TODO

    def get_rating_by_id(self, user_email, timestamp):
        # TODO

    def delete_rating(self, user_email, timestamp):
        # TODO

    def update_rating(self, user_email, timestamp, dish_id, score, comment, created_at):
        # TODO

    def get_ratings_for_dish(self, dish_id):
        # TODO

    def get_ratings_for_user(self, user_email):
        # TODO

    def get_ratings_for_week(self, week_key):
        # TODO

    def get_ratings_for_day(self, day):
        # TODO
        