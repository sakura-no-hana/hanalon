import discord

from .access import is_dev
from .bot import bot, cogs_dir
from .responses import HanalonEmbed


@bot.command()
@is_dev
async def load(ctx, module):
    try:
        bot.load_extension(f'{cogs_dir.name}.{module}')
        await HanalonEmbed(title='Module loaded!',
                           description=f'`{module}` has been loaded successfully!',
                           message=ctx.message).respond(True)
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        error = f'`{module}` is already loaded!'
    except discord.ext.commands.errors.ExtensionNotFound:
        error = f'`{module}` could not be found!'
    e = HanalonEmbed(title='Module not loaded!', description=f'Loading `{module}` failed!',
                     message=ctx.message)
    e.add_field(name='Error', value=error)
    await e.respond(False)


@bot.command()
@is_dev
async def unload(ctx, module):
    try:
        bot.unload_extension(f'{cogs_dir.name}.{module}')
        return await HanalonEmbed(title='Module unloaded!',
                                  description=f'`{module}` has been unloaded successfully!',
                                  message=ctx.message).respond(True)
    except discord.ext.commands.errors.ExtensionNotLoaded:
        error = f'`{module}` is not loaded!'
    e = HanalonEmbed(title='Module not unloaded!', description=f'Unloading `{module}` failed!',
                     message=ctx.message)
    e.add_field(name='Error', value=error)
    await e.respond(False)


@bot.command()
@is_dev
async def reload(ctx, module):
    try:
        bot.reload_extension(f'{cogs_dir.name}.{module}')
        await HanalonEmbed(title='Module reloaded!',
                           description=f'`{module}` has been reloaded successfully!',
                           message=ctx.message).respond(True)
    except discord.ext.commands.errors.ExtensionNotLoaded:
        error = f'`{module}` is not loaded!'
    e = HanalonEmbed(title='Module not reloaded!', description=f'Reloading `{module}` failed!',
                     message=ctx.message)
    e.add_field(name='Error', value=error)
    await e.respond(False)
