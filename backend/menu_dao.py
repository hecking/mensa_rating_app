from dao import DAO

class MenuDAO(DAO):
    def __init__(self, db_path):
        super().__init__(db_path)

    def create_menu_item(self, week_key, day, dish_id):
        # TODO

    def get_menu_item_by_id(self, week_key, day):
        # TODO

    def delete_menu_item(self, week_key, day):
        # TODO
        