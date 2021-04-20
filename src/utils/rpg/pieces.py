from shapely.geometry import Point, Polygon

from utils.rpg.game import Piece


class Wall(Piece):
    def on_coincide(self, movement):
        """Creates a piece for a wall."""
        movement.piece.speed -= float("inf")


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
