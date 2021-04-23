from shapely.affinity import translate
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from utils.rpg.game import DefiniteSkin, Piece, Skin


class Wall(Piece):
    def on_coincide(self, movement, mock=True):
        """Creates a piece for a wall."""
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

    def on_coincide(self, movement, mock=True):
        movement.piece.speed -= float("inf")


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
