from discord.ext import commands

from utils.bot import Context, bot, cogs_dir, include_cog
from utils.responses import HanalonEmbed


class LockedCog(Exception):
    ...


class Cogs(commands.Cog):
    @commands.command()
    @bot.owner_only
    async def load(self, ctx: Context, module: str):
        """
        Loads a cog
        """
        bot.load_extension(f"{cogs_dir.name}.{module}")
        await HanalonEmbed(
            title="Module loaded!",
            description=f"`{module}` has been loaded successfully!",
            context=ctx,
        ).respond(True, override=True)

    @commands.command()
    @bot.owner_only
    async def unload(self, ctx: Context, module: str):
        """
        Unloads a cog
        """
        bot.unload_extension(f"{cogs_dir.name}.{module}")
        if type(self).__name__ not in [type(cog).__name__ for cog in bot.cogs.values()]:
            bot.load_extension(f"{cogs_dir.name}.{module}")
            raise LockedCog(bot.cogs.values())

        await HanalonEmbed(
            title="Module unloaded!",
            description=f"`{module}` has been unloaded successfully!",
            context=ctx,
        ).respond(True, override=True)

    @commands.command()
    @bot.owner_only
    async def reload(self, ctx: Context, module: str):
        """
        Reloads a cog
        """
        bot.reload_extension(f"{cogs_dir.name}.{module}")
        await HanalonEmbed(
            title="Module reloaded!",
            description=f"`{module}` has been reloaded successfully!",
            context=ctx,
        ).respond(True, override=True)

    def cog_unload(self):
        raise LockedCog


def setup(_):
    include_cog(Cogs)
