import random

import d20
import discord
from discord.ext import commands, slash

from utils.bot import include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class Gambling(commands.Cog):
    SUITS = ("♥", "♣", "♠", "♦", "🃏")
    CARDS = (
        "🇦",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "🔟",
        "🇯",
        "🇶",
        "🇰",
    )

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

    @commands.command()
    async def draw(self, ctx: commands.Context, joker: bool = False):
        """
        Draws a card.
        """
        if joker:
            card = (
                Gambling.CARDS[(value := random.randrange(54)) % 13]
                + Gambling.SUITS[value // 13]
            )
            if (color := value // 13) == 5:
                card = ("🟥" if color == 0 else "⬛") + card[1]
        else:
            card = (
                Gambling.CARDS[(value := random.randrange(52)) % 13]
                + Gambling.SUITS[value // 13]
            )

        await HanalonEmbed(
            title="Cards",
            description=card,
            context=ctx,
        ).respond(True)

    @slash.cmd(name="draw")
    async def _draw(
        self,
        ctx: slash.Context,
        joker: slash.Option(
            description="joker",
            required=False,
            type=slash.ApplicationCommandOptionType.BOOLEAN,
        ) = False,
    ):
        """
        Draws a card.
        """
        if joker:
            card = (
                Gambling.CARDS[(value := random.randrange(54)) % 13]
                + Gambling.SUITS[value // 13]
            )
            if (color := value // 13) == 5:
                card = ("🟥" if color == 0 else "⬛") + card[1]
        else:
            card = (
                Gambling.CARDS[(value := random.randrange(52)) % 13]
                + Gambling.SUITS[value // 13]
            )

        await HanalonEmbed(
            title="Cards",
            description=card,
            context=ctx,
        ).respond()


def setup(bot):
    include_cog(bot, Gambling)
