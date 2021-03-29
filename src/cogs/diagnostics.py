import discord
from discord.ext import commands

from utils.access import is_dev

class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_dev
    async def ping(self, ctx, precision='4'):
        e = discord.Embed(title='🏓 Pong!',
                          description=f'{("%." + precision + "f") % self.bot.latency} seconds!',
                          timestamp=ctx.message.created_at, color=0xb9b6ed)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Diagnostics(bot))
