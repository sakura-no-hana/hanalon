from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
import queue
from typing import Any, Iterable

import numpy
import numpy.linalg
from shapely.affinity import translate
from shapely.geometry import Polygon, box
from shapely.ops import nearest_points, unary_union

from utils.rpg.db import RPGException
from utils.rpg.piece import Piece


class InsufficientSpeed(RPGException):
    ...


@dataclass
class Movement:
    x: Number
    y: Number
    piece: Piece
    dungeon: Dungeon
    mode: Any = None

    def __post_init__(self):
        self.vector = numpy.array([float(self.x), float(self.y)])


class Turn(queue.Queue):
    def __init__(self, focus=None):
        super().__init__()

        self.focus = focus

    def do_next(self, *args, **kwargs):
        self.get()(*args, **kwargs)


class TurnManager(queue.Queue):
    def __init__(self, dungeon):
        super().__init__()

        self.turn = None
        self.dungeon = dungeon

    def put(self, *args, **kwargs):
        super().put(*args, **kwargs)
        if self.turn is None:
            self.turn = self.next_turn()

    def next_turn(self):
        if self.empty():
            raise queue.Empty
        else:
            try:
                self.turn.focus.on_turn(self.dungeon)
                self.put(Turn(self.turn.focus))
            except AttributeError:
                ...
        self.turn = self.get()
        return self.turn


@dataclass
class Dungeon:
    pieces: Iterable[Iterable[Iterable[Piece]]]
    default: str = "⬛"

    def __post_init__(self):
        self.turns = TurnManager(self)

    def get_collisions(self, movement):
        piece = movement.piece
        hitbox = piece.move_hitbox(movement)

        collisions = []

        for layer in self.pieces:
            for obj in layer:
                if obj is movement.piece:
                    continue
                if hitbox.intersects(obj.true_hitbox()):
                    collisions.append(obj)

        def collision_distance(piece):
            return numpy.linalg.norm(
                numpy.array(
                    nearest_points(piece.hitbox, movement.piece.hitbox)[0].coords[0]
                )
                - movement.piece.loc
            )

        collisions.sort(key=collision_distance)

        return collisions

    def collide(self, movement, mock):
        collisions = self.get_collisions(movement)

        for obj in collisions:
            if not mock:
                self.turns.turn.put(lambda: obj.on_coincide(movement, mock=mock))
            else:
                obj.on_coincide(movement, mock=mock)

    def move(self, movement):
        test = numpy.copy(movement.vector)
        mag = numpy.linalg.norm(test)

        if mag > movement.piece.speed:
            raise InsufficientSpeed

        if mag == 0:
            movement.piece.on_move(movement)
            return

        test /= 2 * mag

        self.collide(movement, mock=True)

        if movement.piece._speed < 0:
            movement.piece._speed = movement.piece.speed
            raise InsufficientSpeed

        self.turns.turn.put(lambda: movement.piece.on_move(movement))

        self.collide(movement, mock=False)

    def start_turn(self):
        self.turns.next_turn()

    def resolve_turn(self):
        while not self.turns.turn.empty():
            self.turns.turn.do_next()

    def render(self, width, height, origin):
        x, y = origin
        dx, dy = (width - 1) // 2, (height - 1) // 2
        out = [[None for _ in range(width)] for _ in range(height)]
        x, y = x - dx, y - dy

        for layer in self.pieces:
            for obj in layer:
                coords = numpy.rint(obj.loc)

                obj_bounds = obj.skin.get_bounds()

                if obj_bounds:
                    for row in obj_bounds[1][
                        max(round(y - coords[1]), 0) : max(
                            min(round(y + height - coords[1]), len(obj_bounds[1])), 0
                        )
                    ]:
                        for col in obj_bounds[0][
                            max(round(x - coords[0]), 0) : max(
                                min(round(x + width - coords[0]), len(obj_bounds[0])), 0
                            )
                        ]:
                            if px := obj.skin.get_index(col, row):
                                out[row + round(coords[1] - y)][
                                    col + round(coords[0] - x)
                                ] = px
                else:
                    for row in range(
                        round(y - coords[1]), round(y + height - coords[1])
                    ):
                        for col in range(
                            round(x - coords[0]), round(x + width - coords[0])
                        ):
                            if px := obj.skin.get_index(col, row):
                                out[row + round(coords[1] - y)][
                                    col + round(coords[0] - x)
                                ] = px

        for i, row in enumerate(out):
            for j, px in enumerate(row):
                if not out[i][j]:
                    out[i][j] = self.default

        return out

    def render_str(self, width, height, origin):
        board = self.render(width, height, origin)
        board.reverse()
        return "\n".join(["".join(a) for a in board])
