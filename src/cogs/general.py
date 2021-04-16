from typing import Optional

import discord
from discord.ext import commands

from utils.bot import bot, include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class General(commands.Cog):
    @commands.command()
    async def ping(self, ctx: commands.Context, precision: int = 4):
        """
        Returns the ping to a specified precision. Defaults to nearest 10⁻⁴ seconds.
        """
        await HanalonEmbed(
            title="🏓 Pong!",
            description=f'{("%." + str(precision) + "f") % bot.latency} seconds!',
            context=ctx,
        ).respond(True)

    @commands.group()
    async def about(self, ctx: commands.Context):
        """
        Shows information about things. Without any subcommands, it shows the bot's information.
        """
        if ctx.invoked_subcommand is None:
            e = HanalonEmbed(
                ctx,
                title="About me",
                description="Hello! I'm Hanalon, your friendly Adventurers' Guild receptionist! Don't hesitate to consult me if you need anything!",
            )
            e.set_thumbnail(url=bot.user.avatar_url)
            e.add_field(
                name="Version",
                value="I'm not that mature yet… only v0.0.1…",
                inline=False,
            )
            e.add_field(
                name="Library",
                value="I'm a homunculus made with discord.py!",
                inline=False,
            )
            devs = [await bot.fetch_user(dev) for dev in bot.owner_ids]
            e.add_field(
                name="Developers",
                value="I loyally serve my masters: "
                + ", ".join([f"{dev.name}#{dev.discriminator}" for dev in devs]),
                inline=False,
            )
            e.add_field(
                name="Servers",
                value=f"I proudly serve {len(bot.guilds)} Guild branches!",
                inline=False,
            )
            e.add_field(
                name="Users",
                value=f"I am the receptionist for {len(bot.users)} parties!",
                inline=False,
            )
            await e.respond(True)

    @about.command()
    async def party(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """
        Unimplemented
        """
        if user is None:
            user = ctx.message.author
        await ctx.send(user.name)

    @about.command()
    async def guild(self, ctx: commands.Context):
        """
        Unimplemented
        """
        await ctx.send(ctx.message.guild.name)


def setup(_):
    include_cog(General)
