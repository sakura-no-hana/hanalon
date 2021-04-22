from shapely.geometry import Point, Polygon

from utils.rpg.game import DefiniteSkin, MergedPiece, Piece, Skin


class Wall(Piece):
    def on_coincide(self, movement):
        """Creates a piece for a wall."""
        movement.piece.speed -= float("inf")


class MergedWalls(MergedPiece):
    on_coincide = Wall.on_coincide

    def __init__(self, walls, wall_token="#", skin="🟥", *args, **kwargs):
        self._walls = []

        for i, row in enumerate(walls.split()):
            for j, tile in enumerate(row):
                if tile == wall_token:
                    self._walls.append(Piece(j, i, skin=DefiniteSkin([[skin]])))

        super().__init__(self._walls, *args, **kwargs)

        del self._walls

        self.skin.get_bounds = lambda: (range(j + 1), range(i + 1))


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

    def on_coincide(self, movement):
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
        super().__init__(skin_alg=lambda x, y: skin, *args, **kwargs)
