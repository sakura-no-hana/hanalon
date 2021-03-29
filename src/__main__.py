import datetime
import os

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='$')


@bot.command()
async def ping(ctx):
    e = discord.Embed(title='🏓 Pong!', description=f'{"%.4f" % bot.latency} seconds!',
                      timestamp=ctx.message.created_at, color=0xb9b6ed)
    e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                 icon_url=ctx.author.avatar_url)
    await ctx.send(embed=e)


bot.run(os.environ['TOKEN'])
