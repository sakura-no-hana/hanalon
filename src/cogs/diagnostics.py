import re

import discord
from discord.ext import commands

from utils.access import is_dev
from utils.responses import HanalonEmbed, HanalonResponse


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
        guild = ctx.guild
        if match := re.match(r'<#([0-9]+)>$', msg.split()[0]):
            channel_id = int(match.group(1))
            if guild:
                channel = guild.get_channel(channel_id)
                if channel.permissions_for(ctx.author).send_messages and channel.permissions_for(
                        ctx.guild.me).send_messages:
                    await HanalonResponse(query=ctx.message, success=True).send()
                    return await channel.send(
                        embed=HanalonEmbed(title=' '.join(msg.split()[1:]), message=ctx.message))
                return await HanalonResponse(query=ctx.message, success=False).send()
            else:
                return await HanalonResponse(query=ctx.message, success=False).send()
        if len(msg) > 256:
            await HanalonResponse(query=ctx.message, success=False).send()
        else:
            await HanalonEmbed(title=msg, message=ctx.message).respond(True)


def setup(bot):
    bot.add_cog(Diagnostics(bot))
