from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
from typing import TYPE_CHECKING, Any, Callable, Iterable

import numpy
from shapely.affinity import translate
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from utils.rpg.dungeon.skin import DefiniteSkin, Skin

if TYPE_CHECKING:
    from utils.rpg.dungeon.game import Dungeon, Movement
    from utils.rpg.dungeon.ray import Ray


@dataclass
class Piece:
    loc: Iterable[Number] = (0.0, 0.0)
    speed: Number = 0.0
    hitbox: BaseGeometry = box(-0.5, -0.5, 0.5, 0.5)
    skin: Skin = DefiniteSkin([["⬛"]])
    data: Any = None

    def __post_init__(self):
        self.loc = numpy.array(self.loc[:2])
        self.speed = float(self.speed)
        self.max_speed = self.speed
        self._speed = self.speed

    def on_coincide(self, movement: Movement, mock: bool = True):
        ...

    def on_turn(self, dungeon: Dungeon):
        self.speed = self.max_speed
        self._speed = self.max_speed

    def on_move(self, movement: Movement):
        self.loc += movement.vector
        self.speed -= numpy.linalg.norm(movement.vector)

    def on_sight(self, ray: Ray):
        ...

    def true_hitbox(self):
        return translate(self.hitbox, *self.loc)

    def move_hitbox(self, movement: Movement):
        coords = list(self.true_hitbox().exterior.coords)
        pairs = [numpy.array([x, y]) for x, y in zip(coords, coords[1:])]

        def gen_quad(pair, vector):
            return Polygon([pair[0], pair[1], pair[1] + vector, pair[0] + vector])

        polys = []

        for pair in pairs:
            polys.append(gen_quad(pair, movement.vector))

        return unary_union(polys)


class MergedPiece(Piece):
    def __init__(self, pieces: Iterable[Piece], *args, **kwargs):
        """Creates a single piece which simulates multiple pieces. Keep in mind that hooks are overwritten."""
        super().__init__(*args, **kwargs)

        self._pieces = []

        for p in pieces:
            self._pieces.append(
                Piece(x=p.loc[0], y=p.loc[1], hitbox=p.hitbox, skin=p.skin)
            )

        self.skin = Skin()

        def get_tile(x, y):
            for piece in self._pieces:
                if tile := piece.skin.get_index(x - piece.loc[0], y - piece.loc[1]):
                    return tile
            return None

        self.skin.get_index = get_tile

        # bounds should be overridden for further optimization; i cba to write the algorithm
        self.skin.get_bounds = lambda: False

        self.hitbox = unary_union([piece.true_hitbox() for piece in self._pieces])


class Wall(Piece):
    def on_coincide(self, movement: Movement, mock: bool = True):
        if mock:
            movement.piece._speed -= float("inf")
        else:
            movement.piece.speed -= float("inf")


class MergedWalls(Wall):
    def __init__(
        self, walls: str, wall_token: str = "#", skin: str = "🟥", *args, **kwargs
    ):
        """Creates a piece that simulates many individual walls."""
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
    def __post_init__(self):
        super().__post_init__()
        self.hitbox = Polygon()


class Being(Piece):
    def __post_init__(self):
        super().__post_init__()
        self.hitbox = Point(0, 0).buffer(0.125)

    def on_coincide(self, movement: Movement, mock: bool = True):
        if mock:
            movement.piece._speed -= float("inf")
        else:
            movement.piece.speed -= float("inf")


class Plane(Piece):
    def __init__(self, skin_alg: Callable, *args, **kwargs):
        """Creates an infinite non-colliding piece."""
        super().__init__(*args, **kwargs)
        self.hitbox = Polygon()

        self.skin = Skin()
        self.skin.get_bounds = lambda: False
        self.skin.get_index = skin_alg


class BoringPlane(Plane):
    def __init__(self, skin: str, *args, **kwargs):
        """Creates an infinite non-colliding piece with a uniform skin."""
        super().__init__(skin_alg=lambda *_: skin, *args, **kwargs)
