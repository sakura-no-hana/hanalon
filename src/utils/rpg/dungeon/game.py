from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
import queue
from typing import Any, Iterable, Optional

import numpy
import numpy.linalg
from shapely.ops import nearest_points

from utils.rpg import RPGException
from utils.rpg.dungeon.piece import Piece
from utils.rpg.dungeon.ray import Ray


class InsufficientSpeed(RPGException):
    ...


@dataclass
class Movement:
    vector: Iterable[Number]
    piece: Piece
    dungeon: Dungeon
    mode: Any = None

    def __post_init__(self):
        self.vector = numpy.array(self.vector[:2])


class Turn(queue.Queue):
    def __init__(self, focus: Piece = None):
        super().__init__()

        self.focus = focus

    def do_next(self, *args, **kwargs):
        """Does the next action in the turn."""
        self.get()(*args, **kwargs)


class TurnManager(queue.Queue):
    def __init__(self, dungeon: Dungeon):
        super().__init__()

        self.turn = None
        self.dungeon = dungeon

    def put(self, *args, **kwargs):
        """Puts a new turn, advancing to that turn if no turn is present."""
        super().put(*args, **kwargs)
        if self.turn is None:
            self.turn = self.next_turn()

    def next_turn(self):
        """Advances to the next turn, putting a turn with the same focus back into the queue."""
        if self.empty() and not self.turn:
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

    def get_collisions(self, movement: Movement) -> queue.PriorityQueue:
        """Gets all piece collisions, sorted by distance from piece origin."""
        piece = movement.piece
        hitbox = piece.move_hitbox(movement)

        collisions = queue.PriorityQueue()

        for layer in self.pieces:
            for obj in layer:
                if obj is piece:
                    continue
                if hitbox.intersects(obj.true_hitbox()):
                    collisions.put(
                        (
                            numpy.linalg.norm(
                                numpy.array(
                                    nearest_points(
                                        piece.true_hitbox(),
                                        obj.true_hitbox().intersection(hitbox),
                                    )[0].coords[0]
                                )
                                - piece.loc
                            ),
                            obj,
                        )
                    )

        return collisions

    def collide(self, movement: Movement, mock: bool) -> None:
        """Simulates collisions."""
        collisions = self.get_collisions(movement)

        while not collisions.empty():
            obj = collisions.get()[1]
            if not mock:
                self.turns.turn.put(lambda: obj.on_coincide(movement, mock=mock))
            else:
                obj.on_coincide(movement, mock=mock)

    def move(self, movement: Movement) -> None:
        """Moves a piece according to the movement."""
        mag = numpy.linalg.norm(numpy.copy(movement.vector))

        if mag > movement.piece.speed:
            raise InsufficientSpeed

        if mag == 0:
            movement.piece.on_move(movement)
            return

        self.collide(movement, mock=True)

        if movement.piece._speed < 0:
            movement.piece._speed = movement.piece.speed
            raise InsufficientSpeed

        self.turns.turn.put(lambda: movement.piece.on_move(movement))

        self.collide(movement, mock=False)

    def start_turn(self):
        """Starts a turn."""
        self.turns.next_turn()

    def resolve_turn(self):
        """Completes all queued actions in a turn."""
        while not self.turns.turn.empty():
            self.turns.turn.do_next()

    def render(
        self,
        width: int,
        height: int,
        origin: Iterable[int],
        focus: Optional[Piece] = None,
    ) -> Iterable[Iterable[str]]:
        """Renders a 2D list for display."""
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
        if not focus:
            for i, row in enumerate(out):
                for j, px in enumerate(row):
                    if not out[i][j]:
                        out[i][j] = self.default

        return out

    def render_str(self, width: int, height: int, origin: Iterable[int]) -> str:
        """Creates string to display board."""
        board = self.render(width, height, origin)
        board.reverse()
        return "\n".join(["".join(a) for a in board])
