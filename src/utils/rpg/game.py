import queue

import numpy
from shapely.affinity import translate
from shapely.geometry import Polygon, box
from shapely.ops import nearest_points, unary_union

from utils.rpg.db import RPGException


class InsufficientSpeed(RPGException):
    ...


class Skin:
    def get_index(self, x, y):
        raise NotImplementedError

    def get_bounds(self):
        raise NotImplementedError


class DefiniteSkin(Skin):
    def __init__(self, skin):
        self._skin = skin
        self._skin.reverse()

    def get_bounds(self):
        return (range(len(self._skin[0])), range(len(self._skin)))

    def get_index(self, x, y):
        bounds = self.get_bounds()
        if y not in bounds[1] or x not in bounds[0]:
            return None
        return self._skin[int(y)][int(x)]


class Piece:
    def __init__(
        self,
        x=0.0,
        y=0.0,
        speed=0.0,
        hitbox=box(-0.5, -0.5, 0.5, 0.5),
        skin=DefiniteSkin([["⬛"]]),
        data=None,
    ):
        """Initializes a piece with the given parameters."""
        self.loc = numpy.array([float(x), float(y)])
        self.max_speed = speed
        self.hitbox = hitbox

        self.skin = skin

        self.data = data

        self.speed = speed

    def on_coincide(self, movement, mock=False):
        ...

    def on_move(self, movement):
        self.loc += movement.vector

    def true_hitbox(self):
        return translate(self.hitbox, *self.loc)

    def move_hitbox(self, movement):
        coords = list(self.true_hitbox().exterior.coords)
        pairs = [numpy.array([x, y]) for x, y in zip(coords, coords[1:])]

        def gen_quad(pair, vector):
            return Polygon([pair[0], pair[1], pair[1] + vector, pair[0] + vector])

        polys = []

        for pair in pairs:
            polys.append(gen_quad(pair, movement.vector))

        return unary_union(polys)


class MergedPiece(Piece):
    def __init__(self, pieces, *args, **kwargs):
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


class Movement:
    def __init__(self, x, y, piece, dungeon, mode=None):
        """Initializes a movement with the piece and vector given."""
        self.vector = numpy.array([float(x), float(y)])
        self.piece = piece
        self.mode = mode


class Turn(queue.Queue):
    def do_next(self, *args, **kwargs):
        self.get()(*args, **kwargs)


class TurnManager(queue.Queue):
    def __init__(self):
        super().__init__()

        self.turn = Turn()

    def next_turn(self):
        if self.empty():
            self.put(Turn())
        self.turn = self.get()
        return self.turn


class Dungeon:
    def __init__(self, layers, default="⬛"):
        """Initializes a dungeon with the given piece layers."""
        self.pieces = layers
        self.default = default
        self.turns = TurnManager()

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

        if movement.piece.speed < 0:
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
                        max(round(y - coords[1]), 0) : min(
                            round(y + height - coords[1]), len(obj_bounds[1])
                        )
                    ]:
                        for col in obj_bounds[0][
                            max(round(x - coords[0]), 0) : min(
                                round(x + width - coords[0]), len(obj_bounds[0])
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
