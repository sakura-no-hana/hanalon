import discord

from .access import is_dev
from .bot import bot, cogs_dir


@bot.command()
@is_dev
async def load(ctx, module):
    try:
        bot.load_extension(f'{cogs_dir.name}.{module}')
        e = discord.Embed(title='Module loaded!',
                          description=f'`{module}` has been loaded successfully!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
    except Exception as err:
        e = discord.Embed(title='Module not loaded!',
                          description=f'Loading `{module}` failed!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        e.add_field(name='Error', value=err)
        await ctx.send(embed=e)


@bot.command()
@is_dev
async def unload(ctx, module):
    try:
        bot.unload_extension(f'{cogs_dir.name}.{module}')
        e = discord.Embed(title='Module unloaded!',
                          description=f'`{module}` has been unloaded successfully!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
    except Exception as err:
        e = discord.Embed(title='Module not unloaded!',
                          description=f'Unloading `{module}` failed!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        e.add_field(name='Error', value=err)
        await ctx.send(embed=e)


@bot.command()
@is_dev
async def reload(ctx, module):
    try:
        bot.reload_extension(f'{cogs_dir.name}.{module}')
        e = discord.Embed(title='Module reloaded!',
                          description=f'`{module}` has been reloaded successfully!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)
    except Exception as err:
        e = discord.Embed(title='Module not reloaded!',
                          description=f'Reloading `{module}` failed!',
                          timestamp=ctx.message.created_at, color=bot.color)
        e.set_footer(text=f'{ctx.author.name}#{ctx.author.discriminator}',
                     icon_url=ctx.author.avatar_url)
        e.add_field(name='Error', value=err)
        await ctx.send(embed=e)
