from discord.ext import commands
from typing import Optional

from .bot import bot, cogs_dir
from .responses import HanalonEmbed

@bot.command(description='Displays all the command of the bot and their descriptions, if \
    applicable. Currently does not include subcommands or commands in `on_message`.')
async def help(ctx: commands.Context, *, command_value: Optional[str]) -> None:
    '''
    Displays all the command of the bot and their descriptions, if
    applicable, currently not including subcommands.
    '''
    # No specific command, simply list out all commands
    if not command_value:
        # Create an embed for further use
        embed = HanalonEmbed(ctx.message, title='Commands', description=None)
        # Grab all loose commands
        value = ''
        for command in bot.commands:
            value += f'{command.name}\n'
        embed.add_field(name='Loose Commands', value=value)
        del value

        # Cycle through all cogs
        for cog_name, cog in bot.cogs.items():
            # Use the list of commands and their descriptions as "value"
            value = ''
            for command in cog.get_commands():
                value += f'{command.name}\n'
            # Use cog_name as "name"
            embed.add_field(name=cog_name, value=value)
        # Send the embed
        await embed.respond(True)
    # Specific command, need a title and description
    else:
        # Search for command
        command = bot.get_command(command_value)
        # If no command found, error message
        if command is None:
            raise ValueError('Command not found')
        # Send command info
        title = f'Command `{command.name}`'
        desc = command.description
        if not desc:
            desc = 'There is no description provided for this command.'
        embed = HanalonEmbed(ctx.message, title=title, description=desc)
        await embed.respond(True)

@help.error
async def help_error(ctx, error):
    '''
    In case the help command goes wrong, there is a useless message to tell
    them that the help command went wrong, at least
    '''
    # Not really well done, but at this point, I'm getting lazy -_-
    if isinstance(error, commands.CommandInvokeError):
        embed = HanalonEmbed(ctx.message, title='Help Error',
                            description='Command not found')
        await embed.respond(False)