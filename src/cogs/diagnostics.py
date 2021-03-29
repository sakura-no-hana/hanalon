import discord
from discord.ext import commands

from utils.access import is_dev


class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, precision='4'):
        e = discord.Embed(title='🏓 Pong!',
                          description=f'{("%." + precision + "f") % self.bot.latency} seconds!',
                          timestamp=ctx.message.created_at, color=self.bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    @is_dev
    async def seppuku(self, ctx):
        e = discord.Embed(title='さよなら〜',
                          timestamp=ctx.message.created_at, color=self.bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
        await self.bot.change_presence(status=discord.Status.invisible)
        await self.bot.logout()

    @commands.command()
    async def echo(self, ctx, *, msg):
        # No fancy discord.Embed objects
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Diagnostics(bot))
