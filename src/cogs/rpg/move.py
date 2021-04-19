from discord.ext import commands

from utils.responses import HanalonEmbed
from utils.rpg.game import Dungeon, InsufficientSpeed, Movement, ObstructedPath
from utils.rpg.pieces import Being, Wall


class GameAction(commands.Cog):
    def __init__(self, bot):
        """Initializes cog for testing RPG movement."""
        self.bot = bot
        self.chara = Being(0, 0, skin=[["<:__:828630739871858719>"]])
        self.chara.speed = 10
        self.chara.max_speed = 10
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
        except ObstructedPath:
            embed.add_field(
                name="Notice", value="There's something in the way!", inline=False
            )
        except InsufficientSpeed:
            embed.add_field(
                name="Notice", value="The destination is too far!", inline=False
            )

        embed.add_field(name="View", value=self.board())

        if error:
            await embed.respond(False)
        else:
            await embed.respond(True, override=True)


def setup(bot):
    bot.add_cog(GameAction(bot))
