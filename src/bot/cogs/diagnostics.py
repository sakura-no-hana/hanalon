import re

import discord
from discord.ext import commands

from utils.discord.bot import bot, include_cog
from utils.discord.responses import HanalonEmbed


class Diagnostics(commands.Cog):
    @commands.command(aliases=("harakiri",))
    @bot.owner_only
    async def seppuku(self, ctx: commands.Context):
        """Kills the bot."""
        await HanalonEmbed(title="さよなら〜", context=ctx).respond(True, override=True)
        await bot.change_presence(status=discord.Status.invisible)
        await bot.close()

    @commands.command()
    async def echo(self, ctx: commands.Context, *, msg: str):
        """Echoes a message in the specified channel (if given). Defaults to same channel."""
        guild = ctx.guild
        channel = ctx.channel
        if len(words := msg.split()) > 1:
            if match := re.match(r"^<#([0-9]+)>$", words[0]):
                channel_id = int(match.group(1))
                if guild:
                    channel = guild.get_channel(channel_id)
                    msg = " ".join(words[1:])
        await HanalonEmbed(description=msg, context=ctx).respond(
            True, destination=channel
        )


def setup(_):
    include_cog(Diagnostics)
