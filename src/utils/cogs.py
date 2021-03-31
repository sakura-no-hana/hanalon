import discord

from .access import is_dev
from .bot import bot, cogs_dir
from .responses import HanalonEmbed


@bot.command()
@is_dev
async def load(ctx, module):
    bot.load_extension(f'{cogs_dir.name}.{module}')
    await HanalonEmbed(title='Module loaded!',
                       description=f'`{module}` has been loaded successfully!',
                       message=ctx.message).respond(True, override=True)


@bot.command()
@is_dev
async def unload(ctx, module):
    bot.unload_extension(f'{cogs_dir.name}.{module}')
    await HanalonEmbed(title='Module unloaded!',
                       description=f'`{module}` has been unloaded successfully!',
                       message=ctx.message).respond(True, override=True)


@bot.command()
@is_dev
async def reload(ctx, module):
    bot.reload_extension(f'{cogs_dir.name}.{module}')
    await HanalonEmbed(title='Module reloaded!',
                       description=f'`{module}` has been reloaded successfully!',
                       message=ctx.message).respond(True, override=True)
