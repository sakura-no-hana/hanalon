from __future__ import annotations

from enum import Enum
from numbers import Number
import queue
from typing import TYPE_CHECKING, Iterable

import numpy
from shapely.geometry import LineString, Point
from shapely.ops import nearest_points

if TYPE_CHECKING:
    from utils.rpg.dungeon.game import Dungeon
    from utils.rpg.dungeon.piece import Piece

CameraBehavior = Enum("CameraBehavior", ["FOLLOW", "DETACH", "SNAP"])


class Ray(object):
    __slots__ = ("start", "end", "intensity", "dungeon", "ignore", "vector", "hitbox")

    def __init__(
        self,
        start: Iterable[Number],
        end: Iterable[Number],
        intensity: Number,
        dungeon: Dungeon,
        ignore: Iterable[Piece],
    ):
        self.start = numpy.array(start[:2])
        self.end = numpy.array(end[:2])

        self.intensity = float(intensity)

        self.vector = self.end - self.start
        self.hitbox = LineString([self.start, self.end])

        self.dungeon = dungeon
        self.ignore = ignore

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


class RayTracer(object):
    __slots__ = ("source", "dungeon", "_traced")
    corners = numpy.array(((0.5, 0.5), (0.5, -0.5), (-0.5, 0.5), (-0.5, -0.5)))

    def __init__(self, dungeon: Dungeon, source: Piece) -> None:
        self.source = source
        self.dungeon = dungeon

        self._traced = dict()

    @property
    def origin(self):
        return self.dungeon.render_origin

    @property
    def size(self):
        return self.dungeon.render_size

    @property
    def dx(self):
        return self.size[0] // 2

    @property
    def dy(self):
        return self.size[1] // 2

    def clear_cache(self):
        self._traced.clear()

    def trace(self):
        field = numpy.zeros(self.size[2::-1], dtype=bool)

        for i in range(self.size[1]):
            for j in range(self.size[0]):
                goal = numpy.array(
                    (self.origin[0] + j - self.dx, self.origin[1] + i - self.dy)
                )

                for corner in RayTracer.corners:
                    destination = goal + corner

                    dest_rep = tuple(int(i) for i in destination)

                    if dest_rep in self._traced:
                        if self._traced[dest_rep]:
                            field[i][j] = True
                            break
                        continue

                    r = Ray(
                        self.source.loc,
                        destination,
                        1,
                        self.dungeon,
                        ignore=(self.source,),
                    )
                    end = r.trace()

                    if Point(destination).distance(Point(end)) <= 0.1:
                        field[i][j] = True
                        self._traced[dest_rep] = True
                        break

                    self._traced[dest_rep] = False

        return field
