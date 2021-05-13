from __future__ import annotations

from numbers import Number
import queue
from typing import Iterable

from discord.ext.commands import EmojiNotFound
import numpy
import numpy.linalg

import utils.discord.emoji
from utils.rpg import RPGException
from utils.rpg.dungeon.piece import Condition, MovementMode, Piece
from utils.rpg.dungeon.ray import CameraBehavior


class InsufficientSpeed(RPGException):
    ...


class Movement(object):
    __slots__ = ("vector", "piece", "dungeon", "mode")

    def __init__(
        self,
        vector: Iterable[Number],
        *,
        piece: Piece,
        dungeon: Dungeon,
        mode: MovementMode = MovementMode.WALKING,
    ):
        self.vector = numpy.array(vector[:2])
        self.piece = piece
        self.dungeon = dungeon
        self.mode = mode


class Turn(queue.Queue, object):
    __slots__ = "focus"

    def __init__(self, focus: Piece = None):
        super().__init__()

        self.focus = focus

    def do_next(self, *args, **kwargs):
        """Does the next action in the turn."""
        self.get()(*args, **kwargs)


class TurnManager(queue.Queue, object):
    __slots__ = ("turn", "dungeon")

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
                if not (self.turn.focus.condition & Condition.DEAD):
                    self.put(Turn(self.turn.focus))
            except AttributeError:
                ...
        self.turn = self.get()
        return self.turn


class Dungeon(object):
    __slots__ = (
        "_pieces",
        "default",
        "blind",
        "turns",
        "render_size",
        "render_origin",
        "render_behavior",
    )

    def __init__(
        self,
        pieces: Iterable[Iterable[Piece]],
        *,
        default: str = ":black_large_square:",
        blind: str = "<:blank:834557109235482686>",
        render_size: Iterable[int] = (9, 9),
        render_origin: Iterable[Number] = (0, 0),
        render_behavior: CameraBehavior = CameraBehavior.FOLLOW,
    ):
        self._pieces = pieces

        self.default = default
        self.blind = blind

        self.render_size = render_size[:2]
        self.render_origin = tuple(int(i) for i in render_origin[:2])
        self.render_behavior = render_behavior

        for piece in set.union(*map(set, pieces)):
            piece.link(self)

        self.turns = TurnManager(self)

    @property
    def pieces(self):
        return self._pieces

    @pieces.setter
    def pieces(self, new: Iterable[Iterable[Piece]]):
        diff = set.union(*map(set, new)).difference(set.union(*map(set, self._pieces)))

        for piece in diff:
            piece.link(self)

        self._pieces = new

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

        movement.piece.on_move(movement, mock=True)

        if movement.piece._speed < 0:
            movement.piece._speed = movement.piece.speed
            raise InsufficientSpeed

        self.turns.turn.put(lambda: movement.piece.on_move(movement))

        self.collide(movement, mock=False)

    def start_turn(self):
        """Starts a turn."""
        self.turns.next_turn()

        if self.render_behavior in {CameraBehavior.SNAP, CameraBehavior.FOLLOW}:
            self.render_origin = tuple(int(i) for i in self.turns.turn.focus.loc)

    def resolve_turn(self):
        """Completes all queued actions in a turn."""
        while self.turns.turn.qsize() != 0:
            self.turns.turn.do_next()

        if self.render_behavior == CameraBehavior.FOLLOW:
            self.render_origin = tuple(int(i) for i in self.turns.turn.focus.loc)

        self.turns.turn.focus.raytracer.clear_cache()

    @property
    def render(self) -> Iterable[Iterable[str]]:
        """Renders a 2D list for display."""
        x, y = self.render_origin
        width, height = self.render_size

        if self.turns.turn.focus.condition & Condition.BLINDED:
            return [[self.blind] * width for _ in range(height)]

        dx, dy = (width - 1) // 2, (height - 1) // 2
        out = [[None] * width for _ in range(height)]
        x, y = x - dx, y - dy

        for layer in self.pieces:
            for obj in layer:
                if not (obj.condition & Condition.INVISIBLE):
                    coords = numpy.rint(obj.loc)

                    obj_bounds = obj.skin.get_bounds()

                    if obj_bounds:
                        for row in obj_bounds[1][
                            max(round(y - coords[1]), 0) : max(
                                min(round(y + height - coords[1]), len(obj_bounds[1])),
                                0,
                            )
                        ]:
                            for col in obj_bounds[0][
                                max(round(x - coords[0]), 0) : max(
                                    min(
                                        round(x + width - coords[0]), len(obj_bounds[0])
                                    ),
                                    0,
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

        rays = self.turns.turn.focus.raytracer.trace()

        out = [
            [
                utils.discord.emoji.condense(
                    self.blind if not rays[i][j] else self.default if not px else px
                )
                for j, px in enumerate(row)
            ]
            for i, row in enumerate(out)
        ]

        return out

    @property
    def render_str(self) -> str:
        """Creates string to display board."""
        board = self.render
        board.reverse()
        return "\n".join(["".join(a) for a in board])
