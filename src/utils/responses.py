import discord

from .bot import bot


class HanalonEmbed(discord.Embed):
    def __init__(self, message, title=None, description=None, color=bot.color, url=None):
        super().__init__(title=title, description=description, color=color, url=url)
        self.timestamp = message.created_at
        self.set_footer(text=f'{message.author.name}#{message.author.discriminator}',
                        icon_url=message.author.avatar_url)
        self.message = message

    async def respond(self, code=None, override=False, destination=None):
        response = HanalonResponse(self.message, code, override, destination)

        if self.message.channel.permissions_for(self.message.guild.me).embed_links:
            await response.send(embed=self)
        elif self.message.channel.permissions_for(self.message.guild.me).manage_webhooks:
            pfp = await bot.user.avatar_url.read()
            webhook = await self.message.channel.create_webhook(
                name=self.message.guild.me.display_name, avatar=pfp, reason="I can't send embeds…")
            await webhook.send(embed=self)
            await webhook.delete()

            # can't be bothered to deal with reaction logic. try/except is the simplest way to
            # handle reactions.
            try:
                await response.send()
            except discord.Forbidden:
                pass
        elif self.message.channel.permissions_for(self.message.guild.me).send_messages:
            if self.title:
                title_proxy = f'**{self.title}**'
            else:
                title_proxy = ''
            message = f'{title_proxy}\n{self.description}\n'
            for field in self.fields:
                message += f'*{field.name}*\n{field.value}\n'
            try:
                await response.send(message)
            except discord.Forbidden:
                pass
        else:
            raise discord.Forbidden


class HanalonResponse:
    def __init__(self, query, success=None, override_success=False, destination=None):
        self.query = query
        self.success = success
        self.override = override_success
        self.destination = destination

    async def send(self, *args, **kwargs):
        if args or kwargs:
            kwargs['mention_author'] = False
            try:
                if isinstance(self.destination, discord.abc.Messageable):
                    await self.destination.send(*args, **kwargs)
                else:
                    await self.query.reply(*args, **kwargs)
            except Exception as err:
                if not self.override:
                    raise err
        if self.success:
            await self.query.add_reaction(bot.success)
        elif self.success is not None:
            await self.query.add_reaction(bot.failure)
