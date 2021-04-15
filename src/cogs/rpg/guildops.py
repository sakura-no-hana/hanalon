from discord.ext import commands

from utils.bot import bot, include_cog, is_response
from utils.responses import HanalonEmbed
from utils.rpg.db import Character, Clan, Job, Party, Race


class GuildOps(commands.Cog):
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
            await ctx.invoke(bot.get_command("register party"))

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
            check=lambda message: is_response(ctx, message, class_query.response),
        )
        race_query = HanalonEmbed(
            ctx,
            description=f"Please choose a race: {', '.join([race.name.lower() for race in Race])}.",
        )
        await race_query.respond()
        r = await bot.wait_for(
            "message",
            check=lambda message: is_response(ctx, message, race_query.response),
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

    @register.command(name="clan")
    async def _clan(self, ctx: commands.Context, *, name: str):
        await Clan.register(ctx.author, name)
        await HanalonEmbed(
            ctx,
            title=f"Welcome, {name}!",
            description=f"{name} has successfully been registered as a clan!",
        ).respond(True)


def setup(_):
    include_cog(GuildOps)
    bot.characters = bot.db["character"]
    bot.parties = bot.db["party"]
    bot.clans = bot.db["clan"]
    bot.shop = bot.db["shop"]
