from shapely.affinity import translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from utils.rpg.game import DefiniteSkin, Piece, Skin


class Wall(Piece):
    def on_coincide(self, movement, mock=True):
        if mock:
            movement.piece._speed -= float("inf")
        else:
            movement.piece.speed -= float("inf")


class MergedWalls(Wall):
    def __init__(self, walls, wall_token="#", skin="🟥", *args, **kwargs):
        self._skin = []
        self._hb = []

        for i, row in enumerate(walls.split()):
            self._skin.append([])
            for j, tile in enumerate(row):
                if tile == wall_token:
                    self._skin[i].append(skin)
                    self._hb.append(box(-0.5 + j, -0.5 - i, 0.5 + j, 0.5 - i))
                else:
                    self._skin[i].append(None)

        super().__init__(*args, **kwargs)

        self.skin = DefiniteSkin(self._skin)
        self.hitbox = translate(unary_union(self._hb), 0, i)

        del self._skin, self._hb


class Surface(Piece):
    def __init__(self, *args, **kwargs):
        """Creates a piece for a surface (e.g. floor)."""
        super().__init__(*args, **kwargs)
        self.hitbox = Polygon()


class Being(Piece):
    def __init__(self, *args, **kwargs):
        """Creates a piece for a living creature."""
        super().__init__(*args, **kwargs)
        self.hitbox = Point(0, 0).buffer(0.125)

        self.stats = {
            "atk": 100,
            "def": 5,
            "max_hp": 10000,
            # etc.
        }
        self.equipped = []
        self.effects = []  # Only storing non-item effects

    def on_coincide(self, movement, mock=True):
        if mock:
            movement.piece._speed -= float("inf")
        else:
            movement.piece.speed -= float("inf")

    def equip(self, item):
        self.equipped.append(item)
        item.equip_on(self)

    def unequip(self, item):
        self.equipped.remove(item)
        item.unequip()

    def getstats(self) -> dict:
        """Get stats after item bonuses"""
        _modified_stats = self.stats.copy()
        for item in self.equipped:
            for s in item.stats.keys():
                if s not in _modified_stats:
                    continue
                item[s] += item.stats[s]
        return _modified_stats
        
    def apply_effects(self):
        """Apply all effects, including items. May cause
        redundancy."""
        for eff in self.effects:
            eff(self)
        for item in self.equips:
            if item.effect:
                item.use_effect(self)


class Plane(Piece):
    def __init__(self, skin_alg, *args, **kwargs):
        """Creates an infinite non-colliding piece."""
        super().__init__(*args, **kwargs)
        self.hitbox = Polygon()

        self.skin = Skin()
        self.skin.get_bounds = lambda: False
        self.skin.get_index = skin_alg


class BoringPlane(Plane):
    def __init__(self, skin, *args, **kwargs):
        super().__init__(skin_alg=lambda *_: skin, *args, **kwargs)
