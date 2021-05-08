from typing import Optional

import discord
from discord.ext import commands

from utils.discord.bot import bot, include_cog
from utils.discord.responses import HanalonEmbed


class General(commands.Cog):
    @commands.command()
    async def ping(self, ctx: commands.Context, precision: int = 4):
        """Returns the ping to a specified precision. Defaults to nearest 10⁻⁴ seconds."""
        await HanalonEmbed(
            title="🏓 Pong!",
            description=f'{("%." + str(precision) + "f") % bot.latency} seconds!',
            context=ctx,
        ).respond(True)

    @commands.group()
    async def about(self, ctx: commands.Context):
        """Shows information about things. Without any subcommands, it shows the bot's information."""
        if ctx.invoked_subcommand is None:
            if ctx.guild:
                shard = ctx.guild.shard_id
            else:
                shard = 0

            e = HanalonEmbed(
                ctx,
                title="About me",
                description="Hello! I'm Hanalon, a homunculus receptionist. Pleased to meet you!",
            )
            e.set_thumbnail(url=bot.user.avatar_url)
            e.add_field(
                name="Version",
                value=bot.__version__,
                inline=False,
            )
            e.add_field(
                name="Shard",
                value=f"Shard #{shard} of {bot.shard_count}",
                inline=False,
            )
            e.add_field(
                name="Library",
                value=f"discord.py {discord.__version__}",
                inline=False,
            )
            devs = [await bot.fetch_user(dev) for dev in bot.owner_ids]
            e.add_field(
                name="Developers",
                value=", ".join([f"{dev.name}#{dev.discriminator}" for dev in devs]),
                inline=False,
            )
            e.add_field(
                name="Players",
                value=f"{await bot.parties.count_documents(filter=dict())} players",
                inline=False,
            )
            await e.respond(True)

    @about.command()
    async def party(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Unimplemented."""
        if user is None:
            user = ctx.message.author
        await ctx.send(user.name)

    @about.command()
    async def guild(self, ctx: commands.Context):
        """Unimplemented."""
        await ctx.send(ctx.message.guild.name)


def setup(_):
    include_cog(General)
