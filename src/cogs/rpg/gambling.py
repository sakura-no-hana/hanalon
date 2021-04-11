import random

import d20
import discord
from discord.ext import commands, slash

from utils.bot import include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class Deck:
    SUITS = ("♡", "♧", "♤", "♢", "🃏")
    CARDS = ("A",) + tuple(str(i) for i in range(2, 11)) + ("J", "Q", "K")


class Gambling(commands.Cog):
    @commands.command()
    async def roll(self, ctx: commands.Context, *, expr: str = "1d6"):
        """
        Rolls dice based on the expression given.
        """
        result = d20.roll(expr)
        await HanalonEmbed(
            title="Dice 🎲",
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
            title="Dice 🎲",
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
                Deck.CARDS[(value := random.randrange(54)) % 13]
                + Deck.SUITS[value // 13]
            )
            if (color := value // 13) == 5:
                card = ("🟥" if color == 0 else "⬛") + card[1]
        else:
            card = (
                Deck.CARDS[(value := random.randrange(52)) % 13]
                + Deck.SUITS[value // 13]
            )

        await HanalonEmbed(
            title="Cards 🎴",
            description=f"**{card}**",
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
                Deck.CARDS[(value := random.randrange(54)) % 13]
                + Deck.SUITS[value // 13]
            )
            if value // 13 == 5:
                card = ("🟥" if value % 13 == 0 else "⬛") + card[1]
        else:
            card = (
                Deck.CARDS[(value := random.randrange(52)) % 13]
                + Deck.SUITS[value // 13]
            )

        await HanalonEmbed(
            title="Cards 🎴",
            description=f"**{card}**",
            context=ctx,
        ).respond()


def setup(_):
    include_cog(Gambling)
