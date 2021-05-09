from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntFlag
from functools import reduce
from numbers import Number
from operator import ior
from queue import PriorityQueue, Queue
from typing import TYPE_CHECKING, Any, Callable, Iterable

import numpy
from shapely.affinity import translate
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.ops import unary_union

from utils.rpg.dungeon.skin import DefiniteSkin, Skin

if TYPE_CHECKING:
    from utils.rpg.dungeon.game import Dungeon, Movement
    from utils.rpg.dungeon.ray import Ray


Condition = IntFlag(
    "Condition",
    [
        "BLINDED",
        "DEAFENED",
        "GRAPPLED",
        "INCAPACITATED",
        "INVISIBLE",
        "PARALYZED",
        "PETRIFIED",
        "POISONED",
        "PRONE",
        "RESTRAINED",
        "STUNNED",
        "UNCONSCIOUS",
        "DEAD",
        "EXHAUSTED_1",
        "EXHAUSTED_2",
        "EXHAUSTED_3",
        "EXHAUSTED_4",
        "EXHAUSTED_5",
    ],
)

Relation = Enum("Relation", ["CHARMED", "FRIGHTENED"])

IMMOBILE = (
    Condition.GRAPPLED
    | Condition.INCAPACITATED
    | Condition.PARALYZED
    | Condition.PETRIFIED
    | Condition.RESTRAINED
    | Condition.UNCONSCIOUS
    | Condition.EXHAUSTED_5
    | Condition.DEAD
)


MovementMode = Enum(
    "MovementMode",
    [
        "WALKING",
        "CLIMBING",
        "SWIMMING",
        "CRAWLING",
        "JUMPING",
        "FLYING",
        "BURROWING",
    ],
)


@dataclass
class Piece:
    loc: Iterable[Number] = (0.0, 0.0)
    speed: Number = 0.0
    hitbox: BaseGeometry = box(-0.5, -0.5, 0.5, 0.5)
    skin: Skin = DefiniteSkin([["*️⃣"]])
    mount: Piece = None
    data: Any = None

    def __post_init__(self):
        self.loc = numpy.array(self.loc[:2])
        self.speed = float(self.speed)
        self.max_speed = self.speed
        self._speed = self.speed

        self.condition = 0

        self.psychology = {Relation.CHARMED: [], Relation.FRIGHTENED: []}

    def apply_conditions(self, *conditions: Iterable[Condition]):
        self.condition |= reduce(ior, conditions)

    def unapply_conditions(self, *conditions: Iterable[Condition]):
        self.condition ^= reduce(ior, conditions)

    def on_coincide(self, movement: Movement, mock: bool = True):
        ...

    def on_turn(self, dungeon: Dungeon):
        self.speed = self.max_speed
        self._speed = self.max_speed

    def on_move(self, movement: Movement, mock: bool = False):
        # TODO: check jumping capability with athletics stat
        if self.mount:
            self.mount.on_move(movement, mock)
            return

        if mock:
            for enemy in self.psychology[Relation.FRIGHTENED]:
                new_loc = movement.vector + self.loc
                if numpy.linalg.norm(new_loc - enemy.loc) < numpy.linalg.norm(
                    self.loc - enemy.loc
                ):
                    self._speed -= float("inf")
                    return

            if self.condition & IMMOBILE or movement.mode in {
                MovementMode.BURROWING,
                MovementMode.FLYING,
            }:
                self._speed -= float("inf")
                return
            elif movement.mode in {
                MovementMode.CLIMBING,
                MovementMode.SWIMMING,
                MovementMode.CRAWLING,
            }:
                self._speed -= 2 * numpy.linalg.norm(movement.vector)
            else:
                self._speed -= numpy.linalg.norm(movement.vector)
        else:
            if movement.mode == MovementMode.CRAWLING and not (
                self.condition & Condition.PRONE
            ):
                self.apply_conditions(Condition.PRONE)
            elif self.condition & Condition.PRONE:
                self.unapply_conditions(Condition.PRONE)

            if self.condition & IMMOBILE or movement.mode in {
                MovementMode.BURROWING,
                MovementMode.FLYING,
            }:
                self.speed -= float("inf")
                return
            elif movement.mode in {
                MovementMode.CLIMBING,
                MovementMode.SWIMMING,
                MovementMode.CRAWLING,
            }:
                self.speed -= 2 * numpy.linalg.norm(movement.vector)
            else:
                self.loc += movement.vector
                self.speed -= numpy.linalg.norm(movement.vector)

    def on_sight(self, intersect: BaseGeometry, ray: Ray):
        ...

    @property
    def true_hitbox(self):
        return translate(self.hitbox, *self.loc)

    def move_hitbox(self, movement: Movement):
        coords = list(self.true_hitbox.exterior.coords)
        pairs = [numpy.array([x, y]) for x, y in zip(coords, coords[1:])]

        def gen_quad(pair, vector):
            return Polygon([pair[0], pair[1], pair[1] + vector, pair[0] + vector])

        polys = []

        for pair in pairs:
            polys.append(gen_quad(pair, movement.vector))

        return unary_union(polys)

    def process_kinesis(
        self,
        hook_queue: Queue,
        ray_box: BaseGeometry,
        origin: Iterable[Number],
        hook: str,
        *args,
        **kwargs,
    ):
        origin = Point(origin[:2])
        hook = eval(f"self.on_{hook}")

        if is_priority := isinstance(hook_queue, PriorityQueue):
            _queue = hook_queue
        else:
            _queue = PriorityQueue()

        intersect = ray_box.intersection(self.true_hitbox)
        if isinstance(intersect, BaseMultipartGeometry):
            for shape in intersect.geoms:
                _queue.put(
                    (
                        origin.distance(shape),
                        lambda *_args, **_kwargs: hook(
                            *args, *_args, **kwargs, **_kwargs
                        ),
                        shape,
                    )
                )
        elif not intersect.is_empty:
            _queue.put(
                (
                    origin.distance(intersect),
                    lambda *_args, **_kwargs: hook(*args, *_args, **kwargs, **_kwargs),
                    intersect,
                )
            )

        if not is_priority:
            while _queue.qsize() != 0:
                hook_queue.put(_queue.get()[1])


class MergedPiece(Piece):
    def __init__(self, pieces: Iterable[Piece], *args, **kwargs):
        """Creates a single piece which simulates multiple pieces. Keep in mind that hooks are overwritten."""
        super().__init__(*args, **kwargs)

        self._pieces = [
            Piece(x=p.loc[0], y=p.loc[1], hitbox=p.hitbox, skin=p.skin) for p in pieces
        ]

        self.skin = Skin()

        def get_tile(x, y):
            for piece in self._pieces:
                if tile := piece.skin.get_index(x - piece.loc[0], y - piece.loc[1]):
                    return tile
            return None

        self.skin.get_index = get_tile

        # bounds should be overridden for further optimization; they're boundless by default because i cba to figure out a good algorithm.
        self.skin.get_bounds = lambda: False

        self.hitbox = unary_union([piece.true_hitbox for piece in self._pieces])


class Wall(Piece):
    def on_coincide(self, movement: Movement, mock: bool = True):
        if mock:
            movement.piece._speed -= float("inf")
        else:
            movement.piece.speed -= float("inf")

    def on_sight(self, intersect: BaseGeometry, ray: Ray):
        ray.intensity -= float("inf")


class MergedWalls(Wall):
    def __init__(
        self, walls: str, wall_token: str = "#", skin: str = "⬜", *args, **kwargs
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
