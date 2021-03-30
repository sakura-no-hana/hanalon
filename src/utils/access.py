import discord
from discord.ext import commands

from .bot import bot


def bot_dev(ctx):
    return ctx.author.id in bot.devs


is_dev = commands.check(bot_dev)
