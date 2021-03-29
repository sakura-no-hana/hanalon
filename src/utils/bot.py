import os
import pathlib

import discord
from discord.ext import commands


def prefix(bot, message):
    return {'$', f'{bot.user.mention.replace("@!", "@")} ',
            f'{bot.user.mention.replace("@!", "@").replace("@", "@!")} '}


bot = commands.Bot(command_prefix=prefix)
bot.color = 0xb9b6ed
bot.success = '🌸'
bot.failure = '💢'
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


def run():
    load_cogs()
    bot.run(os.environ['TOKEN'])
