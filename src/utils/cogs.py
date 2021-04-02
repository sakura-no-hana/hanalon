from discord.ext import commands

from .bot import bot, cogs_dir, Context
from .responses import HanalonEmbed


@bot.command()
@bot.owner_only
async def load(ctx: Context, module: str):
    """
    Loads a cog
    """
    bot.load_extension(f"{cogs_dir.name}.{module}")
    await HanalonEmbed(
        title="Module loaded!",
        description=f"`{module}` has been loaded successfully!",
        context=ctx,
    ).respond(True, override=True)


@bot.command()
@bot.owner_only
async def unload(ctx: Context, module: str):
    """
    Unloads a cog
    """
    bot.unload_extension(f"{cogs_dir.name}.{module}")
    await HanalonEmbed(
        title="Module unloaded!",
        description=f"`{module}` has been unloaded successfully!",
        context=ctx,
    ).respond(True, override=True)


@bot.command()
@bot.owner_only
async def reload(ctx: Context, module: str):
    """
    Reloads a cog
    """
    bot.reload_extension(f"{cogs_dir.name}.{module}")
    await HanalonEmbed(
        title="Module reloaded!",
        description=f"`{module}` has been reloaded successfully!",
        context=ctx,
    ).respond(True, override=True)
