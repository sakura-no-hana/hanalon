import discord
from discord.ext import commands


def bot_dev(ctx):
    return ctx.author.id in {456185622697345034, 393172660630323200}


is_dev = commands.check(bot_dev)
