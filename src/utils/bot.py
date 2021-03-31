import os
import pathlib

import discord
from discord.ext import commands
from dotenv import load_dotenv
import pymongo

load_dotenv()


def prefix(bot, message):
    return {'$', f'<@{bot.user.id}> ',
            f'<@!{bot.user.id}> '}


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.color = 0xb9b6ed
bot.success = '🌸'
bot.failure = '💢'
bot.devs = {456185622697345034, 393172660630323200}
bot.db = pymongo.MongoClient(os.environ['MONGO'])
cogs_dir = pathlib.Path('./cogs')


def load_cogs():
    for root, dirs, files in os.walk(cogs_dir):
        for f in files:
            if (module := (cogs_dir / f)).suffix == '.py':
                bot.load_extension(f'{cogs_dir.name}.{module.stem}')


@bot.listen('on_ready')
async def prepare():
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Activity(name='the Sola bot arena',
                                                        type=discord.ActivityType.competing))


@bot.listen('on_command_error')
async def handle(ctx, error):
    if not isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction(bot.failure)


def run():
    load_cogs()
    bot.run(os.environ['TOKEN'])
