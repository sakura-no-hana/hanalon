from discord.ext import commands

from utils.rpg.game import Dungeon, InsufficientSpeed, Movement, ObstructedPath
from utils.rpg.pieces import Being, Wall


class GameAction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chara = Being(0, 0, skin=[["<:yuniwant:828629768651014195>"]])
        self.chara.speed = 3
        self.chara.max_speed = 3
        self.dungeon = Dungeon(
            [
                [
                    Wall(3, 3, skin=[["🟥"]]),
                    Wall(3, 4, skin=[["🟥"]]),
                    Wall(4, 5, skin=[["🟥"]]),
                ],
                [self.chara],
            ]
        )

    def board(self) -> str:
        board = self.dungeon.render(13, 13, self.chara.loc)
        board.reverse()
        return "\n".join(["".join(a) for a in board])

    @commands.command()
    async def show(self, ctx) -> None:
        """Test command?"""
        await ctx.send(f"{self.board()}")

    @commands.command()
    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        try:
            self.dungeon.move(Movement(delta_x, delta_y, self.chara, "walk"))
        except ObstructedPath:
            await ctx.send("There's something in the way!")
        except InsufficientSpeed:
            await ctx.send("The destination is too far!")
        await ctx.send(f"{self.board()}")


def setup(bot):
    bot.add_cog(GameAction(bot))
