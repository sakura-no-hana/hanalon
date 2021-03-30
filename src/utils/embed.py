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
        await HanalonResponse(self.message, code).send(embed=self)


class HanalonResponse:
    def __init__(self, query, success=None):
        self.query = query
        self.success = success

    async def send(self, **kwargs):
        kwargs['mention_author'] = False
        if self.success:
            await self.query.add_reaction(bot.success)
        elif self.success is not None:
            await self.query.add_reaction(bot.failure)
        await self.query.reply(**kwargs)
