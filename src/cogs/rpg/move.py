from discord.ext import commands

from utils.bot import is_response
from utils.responses import HanalonEmbed
from utils.rpg.game import DefiniteSkin, Dungeon, InsufficientSpeed, Movement
from utils.rpg.pieces import Being, MergedWalls, Wall
from utils.rpg.prefabs import protohero


class GameAction(commands.Cog):
    def __init__(self, bot):
        """Initializes cog for testing RPG movement."""
        self.bot = bot
        self.chara = protohero.PrototypePecorine(x=0, y=0, speed=10)

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

        self.maze = MergedWalls(self.maze, wall_token="X")

        self.maze.loc = (5, 5)

        self.dungeon = Dungeon(
            [
                [self.maze],
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

    @commands.command(name="start-turn")
    async def start_turn(self, ctx):
        self.dungeon.start_turn()

        embed = HanalonEmbed(ctx)
        embed.add_field(name="View", value=self.board())
        await embed.respond(True)

        while self.chara.speed > 0:
            j = await self.bot.wait_for(
                "message",
                check=lambda message: is_response(ctx, message, embed.response),
            )

            contents = j.content.split()

            if contents[0] == "move":
                embed = await self.move(
                    await self.bot.get_context(j), int(contents[1]), int(contents[2])
                )
            else:
                return

    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        error = True
        embed = HanalonEmbed(ctx)
        try:
            self.dungeon.move(
                Movement(delta_x, delta_y, self.chara, self.dungeon, "walk")
            )
            error = False

            self.dungeon.resolve_turn()

            print(self.chara.speed)
        except InsufficientSpeed:
            embed.add_field(
                name="Notice", value="Cannot reach the destination!", inline=False
            )

        embed.add_field(name="View", value=self.board())

        if error:
            await embed.respond(False)
        else:
            await embed.respond(True, override=True)

        return embed


def setup(bot):
    bot.add_cog(GameAction(bot))
