import discord
from discord.ext import commands

from utils.access import is_dev
from utils.embed import HanalonEmbed


class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, precision='4'):
        e = HanalonEmbed(title='🏓 Pong!',
                         description=f'{("%." + precision + "f") % self.bot.latency} seconds!',
                         message=ctx.message)
        await e.respond(True)

    @commands.command()
    @is_dev
    async def seppuku(self, ctx):
        e = HanalonEmbed(title='さよなら〜',
                         message=ctx.message)
        await e.respond(True)
        await self.bot.change_presence(status=discord.Status.invisible)
        await self.bot.logout()

    @commands.command()
    async def echo(self, ctx, *, msg):
        # No fancy discord.Embed objects
        await ctx.send(msg)

def setup(bot):
    bot.add_cog(Diagnostics(bot))
