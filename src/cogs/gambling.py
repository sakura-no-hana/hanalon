import d20
import discord
from discord.ext import commands, slash

from utils.bot import include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context, *, expr: str = "1d6"):
        """
        Rolls dice based on the expression given.
        """
        result = d20.roll(expr)
        await HanalonEmbed(
            title="Dice",
            description=str(result),
            context=ctx,
        ).respond(True)

    @slash.cmd(name="roll")
    async def _roll(
        self,
        ctx: slash.Context,
        expr: slash.Option(
            description="dice expression",
            required=False,
            type=slash.ApplicationCommandOptionType.STRING,
        ) = "1d6",
    ):
        """
        Rolls dice based on the expression given.
        """
        result = d20.roll(expr)
        await HanalonEmbed(
            title="Dice",
            description=str(result),
            context=ctx,
        ).respond()


def setup(bot):
    include_cog(bot, Gambling)
