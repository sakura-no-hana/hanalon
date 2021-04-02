from discord import Embed
from discord.enums import _is_descriptor
from discord.ext import commands
from discord.ext.commands import Bot, Cog, Command, CommandError, DisabledCommand, Group, HelpCommand
from utils.responses import HanalonEmbed

class CustomHelpCommand(HelpCommand):
    '''
    A help command. However, it has yet to be able to handle Cogs and
    Groups.
    '''

    async def send_bot_help(self, mapping: dict):
        msg = {}
        for cog, commands in mapping.items():
            if not commands:
                continue

            title = cog.qualified_name if cog else 'Loose Commands'
            commands_txt = ''
            prefix = self.context.prefix
            for command in commands:
                commands_txt += f'`{prefix}{command.name}`\n'

            msg[title] = commands_txt
        
        embed = HanalonEmbed(self.context.message, title=title)
        for name, value in msg.items():
            embed.add_field(name=name, value=value)
        await embed.respond(True)

    async def send_command_help(self, command: Command) -> None:
        prefix = self.context.prefix
        parent = command.full_parent_name
        name = command.name

        title = 'Command Help: ' + command.qualified_name
        desc = f"{command.help or 'No details provided.'}\n"

        desc += '**Use**: '
        desc += f'`{prefix}{parent} {name}' if parent else f'`{prefix}{name}'
        desc += f' {command.signature}`\n' if command.signature else '`\n'

        aliases = ', '.join([f'`{parent}{alias}`' if parent else f'`{alias}`' for alias in command.aliases])
        if aliases:
            desc += f'**Aliases**: {aliases}\n'

        embed = HanalonEmbed(self.context.message, title=title, description=desc)
        await embed.respond(True)


class Help(Cog):
    '''A cog to implement the help command'''

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.old_help = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self
    
    def cog_unload(self) -> None:
        '''Load back old help command'''
        self.bot.help_command = self.old_help

def setup(bot):
    bot.add_cog(Help(bot))
