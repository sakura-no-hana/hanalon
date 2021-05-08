from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
import queue
from typing import Any, Iterable

import numpy
import numpy.linalg

from utils.rpg import RPGException
from utils.rpg.dungeon.piece import Piece
from utils.rpg.dungeon.ray import RayTracer


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
        if self.qsize() == 0 and not self.turn:
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
    # blind: str = "<:__:834557109235482686>"
    blind: str = "🌫️"

    def __post_init__(self):
        self.turns = TurnManager(self)

    def collide(self, movement: Movement, mock: bool) -> None:
        """Simulates collisions."""
        piece = movement.piece
        sim_queue = queue.PriorityQueue()

        for layer in self.pieces:
            for obj in layer:
                if obj is piece:
                    continue
                if not mock:
                    obj.process_kinesis(
                        self.turns.turn,
                        movement.piece.move_hitbox(movement),
                        movement.piece.loc,
                        "coincide",
                        movement,
                        mock=False,
                    )
                else:
                    obj.process_kinesis(
                        sim_queue,
                        movement.piece.move_hitbox(movement),
                        movement.piece.loc,
                        "coincide",
                        movement,
                        mock=True,
                    )

        while sim_queue.qsize() != 0:
            sim_queue.get()[1]()

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
        while self.turns.turn.qsize() != 0:
            self.turns.turn.do_next()

    def render(
        self,
        width: int,
        height: int,
        origin: Iterable[int],
    ) -> Iterable[Iterable[str]]:
        """Renders a 2D list for display."""
        x, y = origin
        dx, dy = (width - 1) // 2, (height - 1) // 2
        out = [[None] * width for _ in range(height)]
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

        rays = RayTracer((width, height), origin, self.turns.turn.focus, self).field

        for i, row in enumerate(out):
            for j, px in enumerate(row):
                if not rays[i][j]:
                    out[i][j] = self.blind
                elif not out[i][j]:
                    out[i][j] = self.default

        return out

    def render_str(self, width: int, height: int, origin: Iterable[int]) -> str:
        """Creates string to display board."""
        board = self.render(width, height, origin)
        board.reverse()
        return "\n".join(["".join(a) for a in board])
