from utils.rpg.db.character import Stats

HOOKS = [
    "on_attack",
    "on_move",
    "on_defend",
    "on_death",
    "on_kill",
    "on_action",
]
stats_len = Stats.LUCK + 1 - Stats.MAX_HP

class Effect:
    def __init__(self, hook, effect):
        assert hook in HOOKS
        self.hook = hook
        self.effect = effect

    # TODO: will need further implementation as development progresses
    def check_action(self, action):
        if self.hook == action:
            return True
        return False

    def use(self, allies, foes, situation, dungeon, room, humidity,
            unknown_factors, etc):
        # Define per effect/item
        pass

class Item:
    def __init__(self):
        self.stats = [0] * stats_len
        self.user = None
        self.effect = []

    def set_stats(self, stats):
        assert len(stats) == stats_len
        self.stats = stats

    def get_stats(self):
        return self.stats

    def equip_on_this_user(self, entity):
        self.user = entity

    def who_is_this_user(self):
        return self.user

    def add_effect(self, effect: Effect):
        self.effect.append(effect)
    
    def action(self, a, b):
        # To be defined per item
        for c in self.effect:
            if c.check_action("on_" + a):
                c.use(self.user, b, None, None, None, None, None, None)
