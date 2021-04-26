from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
import queue
from typing import TYPE_CHECKING, Iterable

import numpy
from numpy.linalg import norm
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

if TYPE_CHECKING:
    from utils.rpg.dungeon.game import Dungeon


@dataclass
class Ray:
    start: Iterable[Number]
    end: Iterable[Number]
    dungeon: Dungeon

    def __post_init__(self):
        self.start = numpy.array(self.start[:2])
        self.end = numpy.array(self.end[:2])

        self.vector = self.end - self.start
        self.hitbox = LineString([self.start, self.end])

        self.trace = queue.PriorityQueue()

        # self._norm = norm(self.vector)
        # self._unit = self.vector / self._norm

    def obstructions(self) -> queue.PriorityQueue:
        collisions = queue.PriorityQueue()

        for layer in self.dungeon.pieces:
            for obj in layer:
                if self.hitbox.intersects(obj.true_hitbox()):
                    collisions.put(
                        (
                            numpy.linalg.norm(
                                numpy.array(
                                    nearest_points(
                                        Point(self.start),
                                        obj.true_hitbox().intersection(self.hitbox),
                                    )[0].coords[0]
                                )
                                - self.start
                            ),
                            obj,
                        )
                    )

        return collisions


@dataclass
class RayTracer:
    size: Iterable[int]
    origin: Iterable[int]
    dungeon: Dungeon

    def __post_init__(self):
        self.field = numpy.zeros(self.size[:2], dtype=bool)
        self.dx = self.size[0] // 2
        self.dy = self.size[1] // 2

        self.interest_points = set(
            [
                (self.origin[0] - self.dx, y)
                for y in range(
                    self.origin[1] - self.dy,
                    self.origin[1] + self.dy,
                )
            ]
            + [
                (self.origin[0] + self.dx, y)
                for y in range(
                    self.origin[1] - self.dy,
                    self.origin[1] + self.dy,
                )
            ]
            + [
                (x, self.origin[1] - self.dy)
                for x in range(
                    self.origin[0] - self.dx,
                    self.origin[0] + self.dx,
                )
            ]
            + [
                (x, self.origin[1] + self.dy)
                for x in range(
                    self.origin[0] - self.dx,
                    self.origin[0] + self.dx,
                )
            ]
        )
