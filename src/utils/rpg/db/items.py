class Item:
    def __init__(self):
        """Create an Item object; however, stats and
        effects are yet undefined.
        Items are specifically equipables."""
        self.stats = {}
        self.effect = lambda entity: None
        self.user = None

    def set_stat_bonus(self, stats: dict):
        """Set the stat bonuses of an item.
        `stats` should have a dict of the stat to
        the amount it modifies the stat by (add/subtract)"""
        self.stats = stats

    def set_effect(self, effect: function):
        """Set the effect of an item.
        `effect` is a function that takes in the entity
        which it will be modifying
        """
        self.effect = effect

    def use_effect(self, entity):
        """Use the `effect` function on entity. Maybe
        shouldn't be used from with this fn, dunno."""
        (self.effect)(entity)

    def equip_on(self, entity):
        """For internal use"""
        self.user = entity

    def unequip(self):
        """Internal use"""
        self.user = None
