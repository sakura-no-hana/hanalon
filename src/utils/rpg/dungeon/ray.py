from __future__ import annotations

from dataclasses import dataclass
from numbers import Number
import queue
from typing import TYPE_CHECKING, Iterable

import numpy
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

if TYPE_CHECKING:
    from utils.rpg.dungeon.game import Dungeon
    from utils.rpg.dungeon.piece import Piece


@dataclass
class Ray:
    start: Iterable[Number]
    end: Iterable[Number]
    intensity: Number  # we need this for potential view distance implementation. x-ray vision, maybe?
    dungeon: Dungeon
    ignore: Iterable[Piece]

    def __post_init__(self):
        self.start = numpy.array(self.start[:2])
        self.end = numpy.array(self.end[:2])
        self.intensity = float(self.intensity)

        self.vector = self.end - self.start
        self.hitbox = LineString([self.start, self.end])

    def trace(self):
        collisions = queue.PriorityQueue()

        for layer in self.dungeon.pieces:
            for obj in layer:
                if obj in self.ignore:
                    continue
                obj.process_kinesis(
                    collisions, self.hitbox, self.start, "sight", ray=self
                )

        while collisions.qsize() != 0:
            collision = collisions.get()
            collision[1](intersect=collision[2])

            if self.intensity < 0:
                return nearest_points(collision[2], Point(self.start))[0]

        return Point(self.end)


@dataclass
class RayTracer:
    size: Iterable[int]
    origin: Iterable[Number]
    source: Piece
    dungeon: Dungeon

    def __post_init__(self):
        self.field = numpy.zeros(self.size[2::-1], dtype=bool)

        self.origin = tuple(round(i) for i in self.origin)
        self.dx = self.size[0] // 2
        self.dy = self.size[1] // 2

        corners = numpy.array(((0.5, 0.5), (0.5, -0.5), (-0.5, 0.5), (-0.5, -0.5)))

        for i in range(self.size[1]):
            for j in range(self.size[0]):
                goal = numpy.array(
                    (self.origin[0] + j - self.dx, self.origin[1] + i - self.dy)
                )

                for corner in corners:
                    destination = goal + corner

                    r = Ray(
                        self.origin,
                        destination,
                        1,
                        self.dungeon,
                        ignore=(self.source,),
                    )
                    end = r.trace()

                    if Point(destination).distance(Point(end)) <= 0.1:
                        self.field[i][j] = True
                        break
