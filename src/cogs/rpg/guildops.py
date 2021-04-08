import discord
from discord.ext import commands, slash

from utils.bot import bot, include_cog
from utils.responses import HanalonEmbed, HanalonResponse

from .db import Character, Clan, Party


class GuildOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @bot.owner_only
    async def clear(self, ctx: commands.Context):
        await bot.characters.delete_many(dict())
        await bot.parties.delete_many(dict())
        await bot.clans.delete_many(dict())
        await HanalonEmbed(ctx, description="Database cleared!").respond(True)

    @commands.group()
    async def register(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("register party"))

    @register.command(name="party")
    async def _party(self, ctx: commands.Context):
        await Party.register(ctx.author)
        await HanalonEmbed(
            ctx,
            title=f"Welcome, {ctx.author.name}!",
            description="You have successfully registered yourself with the Adventurers' Guild!",
        ).respond(True)


def setup(bot):
    include_cog(bot, GuildOps)
