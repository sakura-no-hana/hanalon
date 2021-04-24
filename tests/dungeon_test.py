import pytest

from utils.rpg.game import Dungeon, InsufficientSpeed, Movement, Piece, Turn
from utils.rpg.piece import Being, Piece, Surface, Wall
from utils.rpg.skin import DefiniteSkin


@pytest.fixture
def setup_dungeon():
    chara = Being(0, 0, speed=5)
    dungeon = Dungeon([[chara]])

    dungeon.turns.put(Turn(chara))

    return chara, dungeon


@pytest.mark.game
class TestHooks:
    def test_coincide(self):
        class HookedPiece(Piece):
            def on_coincide(self, movement, mock):
                self.coincided = True

        a, b = Piece(0, 0, speed=1), HookedPiece(0, 1)
        dungeon = Dungeon([[a, b]])

        dungeon.turns.put(Turn(a))

        dungeon.move(Movement(0, 1, a, dungeon))

        dungeon.resolve_turn()

        assert b.coincided

    def test_move(self):
        class HookedPiece(Piece):
            def on_move(self, movement):
                self.moved = True

        a = HookedPiece(0, 0)
        dungeon = Dungeon([[a]])

        dungeon.turns.put(Turn(a))

        dungeon.move(Movement(0, 0, a, dungeon))

        dungeon.resolve_turn()

        assert a.moved


@pytest.mark.game
class TestDistance:
    def test_far_orthogonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        with pytest.raises(InsufficientSpeed):
            dungeon.move(Movement(0, 10 ** 10, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 0)

    def test_far_diagonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        with pytest.raises(InsufficientSpeed):
            dungeon.move(Movement(3, 4.0001, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 0)

    def test_near_orthogonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.move(Movement(0, 5, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 5)

    def test_near_diagonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.move(Movement(3, 4, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (3, 4)


@pytest.mark.game
class TestCollision:
    def test_far_orthogonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.pieces.append([Wall(0, 5)])

        dungeon.turns.put(Turn(chara))

        dungeon.move(Movement(0, 4, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 4)

    def test_far_diagonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.pieces.append([Wall(0, 2)])

        dungeon.move(Movement(1, 2, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (1, 2)

    def test_near_orthogonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.pieces.append([Wall(0, 1)])

        with pytest.raises(InsufficientSpeed):
            dungeon.move(Movement(0, 4, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 0)

    def test_near_diagonal(self, setup_dungeon):
        chara, dungeon = setup_dungeon

        dungeon.pieces.append([Wall(1, 1)])

        with pytest.raises(InsufficientSpeed):
            dungeon.move(Movement(2, 2, chara, dungeon))

        dungeon.resolve_turn()

        assert tuple(chara.loc) == (0, 0)


@pytest.mark.bot
@pytest.mark.game
class TestRender:
    def test_overlay(self):
        dungeon = Dungeon([[Piece(0, 0)], [Piece(0, 0, skin=DefiniteSkin([["."]]))]])
        assert dungeon.render_str(1, 1, (0, 0))[0][0] == "."

    def test_skin(self):
        dungeon = Dungeon([[Surface(-1, -1, skin=DefiniteSkin([["."] * 3] * 3))]])
        assert all(
            [all([tile == "." for tile in row]) for row in dungeon.render(3, 3, (0, 0))]
        )
