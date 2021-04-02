import discord
from discord.ext import commands

from .bot import bot


def bot_dev(ctx: commands.Context) -> bool:
    """
    Determines whether the message author is the bot's developer
    """
    return ctx.author.id in bot.devs


is_dev = commands.check(bot_dev)
