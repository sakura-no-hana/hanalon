from discord.ext import commands

from utils.responses import HanalonEmbed
from utils.rpg.game import DefiniteSkin, Dungeon, InsufficientSpeed, Movement
from utils.rpg.pieces import Being, Wall


class GameAction(commands.Cog):
    def __init__(self, bot):
        """Initializes cog for testing RPG movement."""
        self.bot = bot
        self.chara = Being(0, 0, skin=DefiniteSkin([["<:__:828630739871858719>"]]))
        self.chara.speed = 10
        self.chara.max_speed = 10

        self.maze = """
            XXXXX.XXXXX
            X.X.......X
            X.X.XXX.X.X
            X...X.X.X.X
            X.XXX.X.X.X
            X.X...X.X.X
            X.XXX.X.XXX
            X.....X...X
            XXX.XXXXX.X
            X...X.....X
            XXXXX.XXXXX
            """

        self.mazelist = []

        for i, row in enumerate(self.maze.split()):
            for j, tile in enumerate(row):
                if tile == "X":
                    self.mazelist.append(Wall(j + 5, i + 5, skin=DefiniteSkin([["🟥"]])))

        self.dungeon = Dungeon(
            [
                [*self.mazelist],
                [self.chara],
            ]
        )

    def board(self) -> str:
        return self.dungeon.render_str(13, 13, self.chara.loc)

    @commands.command()
    async def show(self, ctx) -> None:
        """Test command?"""
        embed = HanalonEmbed(ctx)
        embed.add_field(name="View", value=self.board())
        await embed.respond(True)

    @commands.command()
    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        error = True
        embed = HanalonEmbed(ctx)
        try:
            self.dungeon.move(Movement(delta_x, delta_y, self.chara, "walk"))
            error = False
        except InsufficientSpeed:
            embed.add_field(
                name="Notice", value="Cannot reach the destination!", inline=False
            )

        embed.add_field(name="View", value=self.board())

        if error:
            await embed.respond(False)
        else:
            await embed.respond(True, override=True)


def setup(bot):
    bot.add_cog(GameAction(bot))
