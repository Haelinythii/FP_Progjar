class inventory:
    def __init__(self, list_item, item_database) -> None:
        self.list_item = list_item
        self.item_database = item_database
        self.initiate_all_items()

    def store(self, item, amount):
        self.list_item[item.name] = self.list_item[item.name] + amount

    def initiate_all_items(self):
        material_categories = [self.item_database.foraging_material, self.item_database.hunting_material]
        for category in material_categories:
            for item in category:
                self.list_item[item.name] = 10

    def get_item_amount(self, item):
        return self.list_item[item.name]

    def remove_item(self, item, amount):
        self.list_item[item.name] = self.list_item[item.name] - amount