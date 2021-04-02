from typing import Optional, Union

import discord
from discord.ext import slash

from .bot import bot, Context


class HanalonEmbed(discord.Embed):
    def __init__(
        self,
        context: Context,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Union[discord.Color, int] = bot.color,
        url: Optional[str] = None,
    ):
        super().__init__(title=title, description=description, color=color, url=url)
        if isinstance(context, slash.Context):
            self.timestamp = context.created_at
        else:
            self.timestamp = context.message.created_at
        self.set_footer(
            text=f"{context.author.name}#{context.author.discriminator}",
            icon_url=context.author.avatar_url,
        )
        self.context = context

    async def respond(
        self,
        code: Optional[bool] = None,
        override: bool = False,
        destination: Optional[discord.abc.Messageable] = None,
        flags: Optional[slash.MessageFlags] = None,
        rtype: slash.InteractionResponseType = slash.InteractionResponseType.ChannelMessageWithSource,
    ):
        """
        Sends a response; this deals with replies and reactions, which most bot messages will use.
        """
        if isinstance(self.context, slash.Context):
            await HanalonResponse(self.context).send(
                embed=self, flags=flags, rtype=rtype
            )
        else:
            response = HanalonResponse(self.context, code, override, destination)

            if self.context.channel.permissions_for(self.context.me).embed_links:
                await response.send(embed=self)
            elif self.context.channel.permissions_for(self.context.me).manage_webhooks:
                pfp = await bot.user.avatar_url.read()
                webhook = await self.context.channel.create_webhook(
                    name=self.context.guild.me.display_name,
                    avatar=pfp,
                    reason="I can't send embeds…",
                )
                await webhook.send(embed=self)
                await webhook.delete()

                # can't be bothered to deal with reaction logic. try/except is the simplest way to
                # handle reactions.
                try:
                    await response.send()
                except discord.Forbidden:
                    pass
            elif self.context.channel.permissions_for(self.context.me).send_messages:
                if self.title:
                    title_proxy = f"**{self.title}**"
                else:
                    title_proxy = ""
                message = (
                    f'{title_proxy}\n{self.description if self.description else ""}\n\n'
                )
                for field in self.fields:
                    message += f"*{field.name}*\n{field.value}\n\n"
                try:
                    await response.send(message)
                except discord.Forbidden:
                    pass
            else:
                raise discord.Forbidden


class HanalonResponse:
    def __init__(
        self,
        context: Context,
        success: Optional[bool] = None,
        override_success: bool = False,
        destination: Optional[discord.abc.Messageable] = None,
    ):
        self.context = context
        self.success = success
        self.override = override_success
        self.destination = destination

    async def send(self, *args, **kwargs):
        """
        Sends a response; this deals with replies and reactions, which most bot messages will use.
        """
        if isinstance(self.context, slash.Context):
            await self.context.respond(*args, **kwargs)
        else:
            if args or kwargs:
                kwargs["mention_author"] = False
                try:
                    if isinstance(self.destination, discord.abc.Messageable):
                        await self.destination.send(*args, **kwargs)
                    else:
                        await self.context.reply(*args, **kwargs)
                except Exception as err:
                    if not self.override:
                        raise err
            if self.success:
                await self.context.message.add_reaction(bot.success)
            elif self.success is not None:
                await self.context.message.add_reaction(bot.failure)
