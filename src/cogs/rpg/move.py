from discord.ext import commands

from utils.bot import is_response
from utils.responses import HanalonEmbed
from utils.rpg.game import Dungeon, InsufficientSpeed, Movement, Turn
from utils.rpg.piece import MergedWalls
from utils.rpg.prefabs import protohero


class GameAction(commands.Cog):
    def __init__(self, bot):
        """Initializes cog for testing RPG movement."""
        self.bot = bot

        self.charas = [
            protohero.PrototypePecorine(x=0, y=0, speed=10),
            protohero.PrototypeYuni(x=-2, y=0, speed=10),
            protohero.PrototypeYui(x=0, y=-2, speed=10),
            protohero.PrototypeLuna(x=-4, y=0, speed=10),
            protohero.PrototypeKyaru(x=0, y=-4, speed=10),
        ]

        self.chara = self.charas[0]

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
                [*self.charas],
            ]
        )

        for c in self.charas:
            self.dungeon.turns.put(Turn(c))

    def board(self) -> str:
        return self.dungeon.render_str(13, 13, self.dungeon.turns.turn.focus.loc)

    @commands.command()
    async def show(self, ctx) -> None:
        """Test command?"""
        embed = HanalonEmbed(ctx)
        embed.add_field(
            name="Character",
            value=self.dungeon.turns.turn.focus.__class__.__name__,
            inline=False,
        )
        embed.add_field(
            name="Remaining Distance",
            value=float(self.dungeon.turns.turn.focus.speed),
            inline=False,
        )
        embed.add_field(name="View", value=self.board())
        await embed.respond(True)

        return embed

    @commands.command(name="start-turn")
    async def start_turn(self, ctx):
        self.dungeon.start_turn()

        embed = HanalonEmbed(ctx)
        embed.add_field(name="View", value=self.board())
        await embed.respond(True)

        while True:
            j = await self.bot.wait_for(
                "message",
                check=lambda message: is_response(ctx, message, embed.response),
            )

            contents = j.content.split()

            if contents[0] == "move":
                embed = await self.move(
                    await self.bot.get_context(j), int(contents[1]), int(contents[2])
                )
            elif contents[0] == "next":
                self.dungeon.resolve_turn()
                self.dungeon.turns.next_turn()
                embed = await self.show(await self.bot.get_context(j))
            else:
                return

            # if self.dungeon.turns.turn.focus.speed < 1:
            #     self.dungeon.resolve_turn()
            #     self.dungeon.turns.next_turn()

    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        error = True
        embed = HanalonEmbed(ctx)
        try:
            self.dungeon.move(
                Movement(
                    delta_x,
                    delta_y,
                    self.dungeon.turns.turn.focus,
                    self.dungeon,
                    "walk",
                )
            )
            error = False

            self.dungeon.resolve_turn()

        except InsufficientSpeed:
            embed.add_field(
                name="Notice", value="Cannot reach the destination!", inline=False
            )

        embed.add_field(
            name="Character",
            value=self.dungeon.turns.turn.focus.__class__.__name__,
            inline=False,
        )
        embed.add_field(
            name="Remaining Distance",
            value=float(self.dungeon.turns.turn.focus.speed),
            inline=False,
        )
        embed.add_field(name="View", value=self.board())

        if error:
            await embed.respond(False)
        else:
            await embed.respond(True, override=True)

        return embed


def setup(bot):
    bot.add_cog(GameAction(bot))
