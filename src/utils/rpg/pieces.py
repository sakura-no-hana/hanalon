from shapely.geometry import Point

from utils.rpg.db import RPGException
from utils.rpg.game import Piece


class Immovable(RPGException):
    ...


class Wall(Piece):
    def on_coincide(self, movement):
        movement.piece.speed -= float("inf")

    def on_move(self, movement):
        raise Immovable


class Being(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hitbox = Point(0.5, 0.5).buffer(0.125)

    def on_coincide(self, movement):
        movement.piece.speed -= float("inf")
