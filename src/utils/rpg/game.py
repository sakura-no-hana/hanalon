import numpy
from shapely import affinity
from shapely.geometry import Polygon


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
        self.loc = numpy.array([float(x), float(y)])
        self._speed = speed
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


class Movement:
    def __init__(self, x, y, piece, mode):
        self.vector = numpy.array([float(x), float(y)])
        self.piece = piece
        self.mode = mode


class Dungeon:
    def __init__(self, layers):
        self.pieces = layers

    def add_piece(self, piece, layer):
        self.pieces[layer].append(piece)

    def collide(self, movement):
        piece = movement.piece
        piece_hitbox = affinity.translate(piece.hitbox, *piece.loc)
        collided = False
        for layer in self.pieces:
            for obj in layer:
                if obj is movement.piece:
                    continue
                if piece_hitbox.intersects(affinity.translate(obj.hitbox, *obj.loc)):
                    collided = True
                    obj.on_coincide(movement)
        return collided

    def move(self, movement):
        test = numpy.copy(movement.vector)
        mag = numpy.linalg.norm(test)
        test /= 2 * mag

        origin = numpy.copy(movement.piece.loc)

        while (movement.piece.loc - origin < movement.vector)[
            0
        ] and movement.piece.speed > 0:
            if self.collide(movement):
                movement.piece.loc = origin

            movement.piece.loc += test
            movement.piece.speed -= mag

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
                        if px:
                            out[round(coords[1] - y + i)][round(coords[0] - x + j)] = px

        for i, row in enumerate(out):
            for j, px in enumerate(row):
                if not out[i][j]:
                    out[i][j] = "⬛"

        return out
