import re

import discord
from discord.ext import commands

from utils.access import is_dev
from utils.bot import include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=('harakiri',))
    @is_dev
    async def seppuku(self, ctx: commands.Context):
        """
        Kills the bot.
        """
        await HanalonEmbed(title='さよなら〜', context=ctx).respond(True, override=True)
        await self.bot.change_presence(status=discord.Status.invisible)
        await self.bot.logout()

    @commands.command()
    async def echo(self, ctx: commands.Context, *, msg: str):
        """
        Echoes a message in the specified channel (if given). Defaults to same channel.
        """
        guild = ctx.guild
        channel = ctx.channel
        if len(words := msg.split()) > 1:
            if match := re.match(r'<#([0-9]+)>$', words[0]):
                channel_id = int(match.group(1))
                if guild:
                    channel = guild.get_channel(channel_id)
                    msg = ' '.join(words[1:])
        await HanalonEmbed(title=msg, context=ctx).respond(True, destination=channel)


def setup(bot):
    include_cog(bot, Diagnostics)
