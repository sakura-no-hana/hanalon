from discord.ext.commands import (
    Bot,
    Cog,
    Command,
    Group,
    HelpCommand,
)
from utils.responses import HanalonEmbed


class CustomHelpCommand(HelpCommand):
    """
    A help command. However, it has yet to be able to handle Cogs and
    Groups.
    """

    async def send_bot_help(self, mapping: dict):
        msg = {}
        for cog, commands in mapping.items():
            if not commands:
                continue

            title = cog.qualified_name if cog else "Other"
            commands_txt = ""
            prefix = self.context.prefix
            for command in commands:
                commands_txt += f"`{prefix}{command.name}`\n"

            msg[title] = commands_txt

        embed = HanalonEmbed(self.context, title=title)
        for name, value in msg.items():
            embed.add_field(name=name, value=value)
        await embed.respond(True)
    
    async def send_cog_help(self, cog: Cog):
        name = "Cog Help: " + cog.qualified_name
        description = cog.description + "\n"
        commands_text = "**Commands**\n"
        for c in cog.get_commands():
            c_name = f"{self.context.prefix}{c.qualified_name}"
            if c.signature:
                commands_text += f"`{c_name} {c.signature}`\n"
            else:
                commands_text += f"`{c_name}`\n"
        details = description + commands_text
        embed = HanalonEmbed(self.context, title=name, description=details)
        await embed.respond(True)
    
    async def send_group_help(self, group: Group):
        name = "Group Help: " + group.qualified_name
        description = group.help + "\n"
        commands_text = "**Commands**\n"
        for c in group.commands:
            c_name = f"{self.context.prefix}{c.qualified_name}"
            if c.signature:
                if c.signature:
                    commands_text += f"`{c_name} {c.signature}`\n"
                else:
                    commands_text += f"`{c_name}`\n"
        details = description + commands_text
        embed = HanalonEmbed(self.context, title=name, description=details)
        await embed.respond(True)

    async def send_command_help(self, command: Command) -> None:
        prefix = self.context.prefix
        parent = command.full_parent_name
        name = command.name

        title = "Command Help: " + command.qualified_name
        desc = f"{command.help or 'No details provided.'}\n"

        desc += "**Use**: "
        desc += f"`{prefix}{parent} {name}" if parent else f"`{prefix}{name}"
        desc += f" {command.signature}`\n" if command.signature else "`\n"

        aliases = ", ".join(
            [
                f"`{parent}{alias}`" if parent else f"`{alias}`"
                for alias in command.aliases
            ]
        )
        if aliases:
            desc += f"**Aliases**: {aliases}\n"

        embed = HanalonEmbed(self.context, title=title, description=desc)
        await embed.respond(True)


class Help(Cog):
    """A cog to implement the help command"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.old_help = bot.help_command
        bot.help_command = CustomHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        """Load back old help command"""
        self.bot.help_command = self.old_help


def setup(bot):
    bot.add_cog(Help(bot))
