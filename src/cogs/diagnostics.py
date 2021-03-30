import re

import discord
from discord.ext import commands

from utils.access import is_dev
from utils.responses import HanalonEmbed, HanalonResponse


class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_dev
    async def seppuku(self, ctx):
        await HanalonEmbed(title='さよなら〜', message=ctx.message).respond(True)
        await self.bot.change_presence(status=discord.Status.invisible)
        await self.bot.logout()

    @commands.command()
    async def echo(self, ctx, *, msg):
        guild = ctx.guild
        channel = ctx.channel
        if len(words := msg.split()) > 1:
            if match := re.match(r'<#([0-9]+)>$', words[0]):
                channel_id = int(match.group(1))
                if guild:
                    channel = guild.get_channel(channel_id)
                    msg = ' '.join(words[1:])
        if len(msg) > 256 or not channel.permissions_for(
                ctx.author).send_messages or not channel.permissions_for(
            ctx.guild.me).send_messages:
            return await HanalonResponse(query=ctx.message, success=False).send()
        if ctx.channel == channel:
            return await HanalonEmbed(title=msg, message=ctx.message).respond(True)
        else:
            await HanalonResponse(query=ctx.message, success=True).send()
            return await channel.send(embed=HanalonEmbed(title=msg, message=ctx.message))


def setup(bot):
    bot.add_cog(Diagnostics(bot))
