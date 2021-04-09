import discord
from discord.ext import commands, slash

from utils.bot import bot, include_cog
from utils.responses import HanalonEmbed, HanalonResponse

from .db import Character, Clan, Job, Party, Race


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

    @register.command(name="character")
    async def _character(self, ctx: commands.Context, *, name: str):
        class_query = HanalonEmbed(
            ctx,
            description=f"Please choose a class: {', '.join([job.name.lower() for job in Job])}.",
        )
        await class_query.respond()
        j = await bot.wait_for(
            "message",
            check=lambda message: message.reference.message_id
            == class_query.response.reply.id
            and message.author == ctx.author,
        )
        race_query = HanalonEmbed(
            ctx,
            description=f"Please choose a race: {', '.join([race.name.lower() for race in Race])}.",
        )
        await race_query.respond()
        r = await bot.wait_for(
            "message",
            check=lambda message: message.reference.message_id
            == race_query.response.reply.id
            and message.author == ctx.author,
        )
        try:
            await Character.register(ctx.author, name, j.content, r.content)
        except ValueError as e:
            await HanalonEmbed(
                ctx,
                title=f"Registration failed!",
                description=f"Perhaps your class or race was entered incorrectly?",
            ).respond(False)
            raise e
        await HanalonEmbed(
            ctx,
            title=f"Welcome, {name}!",
            description=f"{name} has successfully been registered as a character!",
        ).respond(True)


def setup(bot):
    include_cog(bot, GuildOps)
