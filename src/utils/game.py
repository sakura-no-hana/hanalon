class Piece:
    def __init__(self, x, y, z, emoji=[["⬛"]], move_cost=0):
        self.loc = (x, y, z)
        self.emoji = emoji
        self.move_cost = move_cost

    def on_move(self, vector, piece=None):
        raise NotImplementedError


class Wall(Piece):
    def __init__(self, x, y, emoji=[["⬛"]]):
        super().__init__(x, y, 0, emoji)

    def on_move(self, vector, piece=None):
        # walls block movement
        return False


class Tile(Piece):
    def __init__(self, x, y, emoji=[["🟫"]]):
        super().__init__(x, y, 0, emoji)

    def on_move(self, vector, piece=None):
        # tiles *usually* don't obstruct movement
        return True


class Board:
    def __init__(self, pieces):
        # pieces should be a 3d list. first 2 dimensions are x & y, third is for overlays.
        self.pieces = pieces
