from discord.ext import commands

from utils.discord.bot import bot, cogs_dir, include_cog
from utils.discord.responses import HanalonEmbed


class LockedCog(Exception):
    ...


class Cogs(commands.Cog):
    @classmethod
    def module(cls, cog: str) -> str:
        return f"{'.'.join(cogs_dir.parts)}.{cog}"

    @commands.command()
    @bot.owner_only
    async def load(self, ctx: commands.Context, module: str):
        """Loads a cog."""
        bot.load_extension(Cogs.module(module))
        await HanalonEmbed(
            title="Module loaded!",
            description=f"`{module}` has been loaded successfully!",
            context=ctx,
        ).respond(True, override=True)

    @commands.command()
    @bot.owner_only
    async def unload(self, ctx: commands.Context, module: str):
        """Unloads a cog."""
        bot.unload_extension(Cogs.module(module))
        if type(self).__name__ not in [type(cog).__name__ for cog in bot.cogs.values()]:
            bot.load_extension(Cogs.module(module))
            raise LockedCog(bot.cogs.values())

        await HanalonEmbed(
            title="Module unloaded!",
            description=f"`{module}` has been unloaded successfully!",
            context=ctx,
        ).respond(True, override=True)

    @commands.command()
    @bot.owner_only
    async def reload(self, ctx: commands.Context, module: str):
        """Reloads a cog."""
        bot.reload_extension(Cogs.module(module))
        await HanalonEmbed(
            title="Module reloaded!",
            description=f"`{module}` has been reloaded successfully!",
            context=ctx,
        ).respond(True, override=True)


def setup(_):
    include_cog(Cogs)
