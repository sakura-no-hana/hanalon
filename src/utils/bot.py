import os
import pathlib

from discord.ext import commands

bot = commands.Bot(command_prefix='$')
bot.color = 0xb9b6ed
cogs_dir = pathlib.Path('./cogs')


def load_cogs():
    for root, dirs, files in os.walk(cogs_dir):
        for f in files:
            if (module := (cogs_dir / f)).suffix == '.py':
                bot.load_extension(f'{cogs_dir.name}.{module.stem}')


def run():
    load_cogs()
    bot.run(os.environ['TOKEN'])
