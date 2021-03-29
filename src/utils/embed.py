import discord

from .bot import bot


class HanalonEmbed(discord.Embed):
    def __init__(self, title, message, description=None, color=bot.color):
        super().__init__(title=title, description=description, color=color)
        self.timestamp = message.created_at
        self.set_footer(text=f'{message.author.name}#{message.author.discriminator}',
                        icon_url=message.author.avatar_url)
        self.message = message

    async def respond(self, code=None):
        if code:
            await self.message.add_reaction(bot.success)
        elif code is not None:
            await self.message.add_reaction(bot.failure)
        await self.message.channel.send(embed=self)
