import discord

from .access import is_dev
from .bot import bot, cogs_dir
from .embed import HanalonEmbed


@bot.command()
@is_dev
async def load(ctx, module):
    try:
        bot.load_extension(f'{cogs_dir.name}.{module}')
        e = HanalonEmbed(title='Module loaded!',
                         description=f'`{module}` has been loaded successfully!',
                         message=ctx.message)
        await e.respond(True)
    except Exception as err:
        e = HanalonEmbed(title='Module not loaded!', description=f'Loading `{module}` failed!',
                         message=ctx.message)
        e.add_field(name='Error', value=err)
        await e.respond(False)


@bot.command()
@is_dev
async def unload(ctx, module):
    try:
        bot.unload_extension(f'{cogs_dir.name}.{module}')
        e = HanalonEmbed(title='Module unloaded!',
                         description=f'`{module}` has been unloaded successfully!',
                         message=ctx.message)
        await e.respond(True)
    except Exception as err:
        e = HanalonEmbed(title='Module not unloaded!', description=f'Unloading `{module}` failed!',
                         message=ctx.message)
        e.add_field(name='Error', value=err)
        await e.respond(False)


@bot.command()
@is_dev
async def reload(ctx, module):
    try:
        bot.reload_extension(f'{cogs_dir.name}.{module}')
        e = HanalonEmbed(title='Module reloaded!',
                         description=f'`{module}` has been reloaded successfully!',
                         message=ctx.message)
        await e.respond(True)
    except Exception as err:
        e = HanalonEmbed(title='Module not reloaded!', description=f'Reloading `{module}` failed!',
                         message=ctx.message)
        e.add_field(name='Error', value=err)
        await e.respond(False)
