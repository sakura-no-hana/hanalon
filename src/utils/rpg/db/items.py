from typing import List

from utils.rpg.db.character import Stats

# Stats list
# XP                  0
# HP                  1   Items add to these stats:
# MAX_HP              2   0
# ARMOR               3   1
# SPEED               4   2
# STRENGTH            5   3
# DEXTERITY           6   4
# CONSTITUTION        7   5
# INTELLIGENCE        8   6
# WISDOM              9   7
# CHARISMA            10  8
# LUCK                11  9
# ACROBATICS          12
# ANIMAL_HANDLING     13
# ARCANA              14
# ATHLETICS           15
# DECEPTION           16
# HISTORY             17
# INSIGHT             18
# INTIMIDATION        19
# INVESTIGATION       20
# MEDICINE            21
# NATURE              22
# PERCEPTION          23
# PERFORMANCE         24
# PERSUATION          25
# RELIGION            26
# SLEIGHT_OF_HAND     27
# STEALTH             28
# SURVIVAL            29

HOOKS = {
    "on_attack",
    "on_move",
    "on_defend",
    "on_death",
    "on_kill",
    "on_action",
}

stats_len = 10  # Stats.LUCK + 1 - Stats.MAX_HP


class Effect:
    def __init__(self, hook: str, effect):
        """
        Currently initializes an effect with a hook and effect
        """
        # Standardize hook format to "on_[something]"
        if not hook.startswith("on_"):
            hook = f"on_{hook}"

        # Ensure valid hook
        assert hook in HOOKS

        self.hook: str = hook
        self.effect = effect

    # TODO: will need further implementation as development progresses
    def check(self, action: str):
        """
        Checks if the action provided corresponds with the effect's
        hook
        """
        if not action.startswith("on_"):
            action = f"on_{action}"
        if self.hook == action:
            return True
        else:
            return False

    # TODO: implement some sort of context
    def use(self, dungeon):
        """
        Activate the effect
        * Currently takes a `dungeon` for context, but this may change
        * Currently assumes effect is a function callable with `dungeon`
        as an argument, which may not be the case. May change
        """
        (self.effect)(dungeon)


class Item:
    def __init__(self):
        """
        Create an item with default attributes.
        All stats will be set to 0. User will be set to `None`. No effects.

        Attributes
        ------
        * `stats` — A list of size `stats_len` (from `MAX_HP` to `LUCK`,
        inclusive)
        * `user` — The user equipping the item or `None`. Does not actually
        check if this is a valid user
        * `effects` — A list of `Effect`. Development in progress.
        """
        self.stats: List[int] = [0] * stats_len
        self.user = None
        self.effects: List[Effect] = []

    @classmethod
    def init(cls, stats, user, effects) -> "Item":
        """
        Initialize an item with stats, user, and effects.
        Raises an error if len(stats) != stats_len.
        Does not check for anything else.
        """
        assert len(stats) == stats_len
        item = Item()
        item.stats = stats
        item.user = user
        item.effects = effects
        return item

    def clone(self) -> "Item":
        """
        Creates a copy of this item.
        """
        return self.init(self.stats, self.user, self.effects)

    def equip_on(self, entity):
        """
        Sets the equipping user of this item (for reference)
        """
        self.user = entity

    def add_effect(self, effect: Effect):
        """
        Adds an effect to the item.
        """
        self.effects.append(effect)

    # TODO: implement some sort of context
    def action(self, trigger, dungeon):
        """
        Use the item for an action. This may be directly or indirectly.
        Currently takes a `trigger` and `dungeon`.
        Work in progress.
        """
        for effect in self.effects:
            if effect.hook == f"on_{trigger}":
                effect.use(dungeon)

    def __str__(self) -> str:
        return f"{self.stats}"


# Some testing
if __name__ == "__main__":
    a = Item.init([0] * 10, None, None)
    a.stats[4] = 100
    b = a.clone()
    print(b)
