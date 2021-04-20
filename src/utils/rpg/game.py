import numpy
from shapely import affinity
from shapely.geometry import Polygon
from shapely.ops import nearest_points, unary_union

from utils.rpg.db import RPGException


class InsufficientSpeed(RPGException):
    ...


class Piece:
    def __init__(
        self,
        x,
        y,
        speed=0.0,
        hitbox=Polygon([(0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)]),
        skin=[["⬛"]],
        data=None,
    ):
        """Initializes a piece with the given parameters."""
        self.loc = numpy.array([float(x), float(y)])
        self.max_speed = speed
        self.hitbox = hitbox

        # note that the skin is rendered upside-down, so we must reverse it
        self.skin = skin
        self.skin.reverse()
        self.data = data

        self.speed = speed

    def on_coincide(self, movement):
        ...

    def on_move(self, movement):
        self.loc += movement.vector

    def move_hitbox(self, movement):
        coords = list(self.hitbox.exterior.coords)
        pairs = [numpy.array([x, y]) for x, y in zip(coords, coords[1:])]

        def gen_quad(pair, vector):
            return Polygon([pair[0], pair[1], pair[1] + vector, pair[0] + vector])

        polys = []

        for pair in pairs:
            polys.append(gen_quad(pair, movement.vector))

        return unary_union(polys)


class Movement:
    def __init__(self, x, y, piece, mode=None):
        """Initializes a movement with the piece and vector given."""
        self.vector = numpy.array([float(x), float(y)])
        self.piece = piece
        self.mode = mode


class Dungeon:
    def __init__(self, layers):
        """Initializes a dungeon with the given piece layers."""
        self.pieces = layers

    def get_collisions(self, movement):
        piece = movement.piece
        hitbox = affinity.translate(piece.move_hitbox(movement), *piece.loc)

        collisions = []

        for layer in self.pieces:
            for obj in layer:
                if obj is movement.piece:
                    continue
                if hitbox.intersects(affinity.translate(obj.hitbox, *obj.loc)):
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

    def collide(self, movement):
        collisions = self.get_collisions(movement)

        for obj in collisions:
            obj.on_coincide(movement)

    def move(self, movement):
        movement.piece.speed = movement.piece.max_speed

        test = numpy.copy(movement.vector)
        mag = numpy.linalg.norm(test)

        if mag > movement.piece.speed:
            raise InsufficientSpeed

        if mag == 0:
            movement.piece.on_move(movement)
            return

        test /= 2 * mag

        self.collide(movement)

        if movement.piece.speed < 0:
            raise InsufficientSpeed

        movement.piece.on_move(movement)

    def render(self, width, height, origin):
        x, y = origin
        dx, dy = (width - 1) // 2, (height - 1) // 2
        out = [[None for _ in range(width)] for _ in range(height)]
        x, y = x - dx, y - dy

        for layer in self.pieces:
            for obj in layer:
                coords = numpy.rint(obj.loc)

                for i, row in enumerate(obj.skin):
                    for j, px in enumerate(row):
                        if (
                            px
                            and 0 <= (vertical := round(coords[1] - y + i)) < height
                            and 0 <= (horizontal := round(coords[0] - x + j)) < width
                        ):
                            out[vertical][horizontal] = px

        for i, row in enumerate(out):
            for j, px in enumerate(row):
                if not out[i][j]:
                    out[i][j] = "⬛"

        return out

    def render_str(self, width, height, origin):
        board = self.render(width, height, origin)
        board.reverse()
        return "\n".join(["".join(a) for a in board])
