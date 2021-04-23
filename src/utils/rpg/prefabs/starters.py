from utils.rpg.items import Item


class Sword(Item):
    def __init__(self):
        super().__init__()
        self.stats = {
            "atk": 10,
        }
