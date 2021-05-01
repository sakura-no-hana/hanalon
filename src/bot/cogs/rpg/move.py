from discord.ext import commands

from utils.discord.bot import is_response
from utils.discord.responses import HanalonEmbed
from utils.rpg.dungeon import Dungeon, InsufficientSpeed, MergedWalls, Movement, Turn
from utils.rpg.prefabs import protohero


class GameAction(commands.Cog):
    def __init__(self, bot):
        """Initializes cog for testing RPG movement."""
        self.bot = bot

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

        self.dungeons = dict()

    def board(self, hash) -> str:
        return self.dungeons[hash].render_str(
            13, 13, self.dungeons[hash].turns.turn.focus.loc
        )

    def create_dungeon(self, hash):
        charas = [
            protohero.PrototypePecorine(loc=(0, 0), speed=10),
            protohero.PrototypeYuni(loc=(-2, 0), speed=10),
            protohero.PrototypeYui(loc=(0, -2), speed=10),
            protohero.PrototypeLuna(loc=(-4, 0), speed=10),
            protohero.PrototypeKyaru(loc=(0, -4), speed=10),
        ]

        self.dungeons[hash] = Dungeon(
            [
                [self.maze],
                [*charas],
            ]
        )

        for c in charas:
            self.dungeons[hash].turns.put(Turn(c))

    @commands.command()
    async def show(self, ctx) -> None:
        """Test command?"""
        embed = HanalonEmbed(ctx)
        embed.add_field(
            name="Character",
            value=self.dungeons[ctx.author.id].turns.turn.focus.__class__.__name__,
            inline=False,
        )
        embed.add_field(
            name="Remaining Distance",
            value=float(self.dungeons[ctx.author.id].turns.turn.focus.speed),
            inline=False,
        )
        embed.add_field(name="View", value=self.board(ctx.author.id))
        await embed.respond(True)

        return embed

    @commands.command(name="start-turn")
    async def start_turn(self, ctx):
        if ctx.author.id not in self.dungeons:
            self.create_dungeon(ctx.author.id)

        self.dungeons[ctx.author.id].start_turn()

        embed = HanalonEmbed(ctx)
        embed.description = f"**View**\n{self.board(ctx.author.id)}"
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
                self.dungeons[ctx.author.id].resolve_turn()
                self.dungeons[ctx.author.id].turns.next_turn()
                embed = await self.show(await self.bot.get_context(j))
            else:
                del self.dungeons[ctx.author.id]
                return

            # if self.dungeons[ctx.author.id].turns.turn.focus.speed < 1:
            #     self.dungeons[ctx.author.id].resolve_turn()
            #     self.dungeons[ctx.author.id].turns.next_turn()

    async def move(self, ctx, delta_x: int, delta_y: int) -> None:
        error = True
        embed = HanalonEmbed(ctx)
        try:
            self.dungeons[ctx.author.id].move(
                Movement(
                    (delta_x, delta_y),
                    self.dungeons[ctx.author.id].turns.turn.focus,
                    self.dungeons[ctx.author.id],
                    "walk",
                )
            )
            error = False

            self.dungeons[ctx.author.id].resolve_turn()

        except InsufficientSpeed:
            embed.add_field(
                name="Notice", value="Cannot reach the destination!", inline=False
            )

        embed.add_field(
            name="Character",
            value=self.dungeons[ctx.author.id].turns.turn.focus.__class__.__name__,
            inline=False,
        )
        embed.add_field(
            name="Remaining Distance",
            value=float(self.dungeons[ctx.author.id].turns.turn.focus.speed),
            inline=False,
        )
        embed.description = f"**View**\n{self.board(ctx.author.id)}"
        if error:
            await embed.respond(False)
        else:
            await embed.respond(True, override=True)

        return embed


def setup(bot):
    bot.add_cog(GameAction(bot))
