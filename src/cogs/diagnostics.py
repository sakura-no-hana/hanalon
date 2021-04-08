import re

import discord
from discord.ext import commands

from utils.bot import bot, include_cog
from utils.responses import HanalonEmbed, HanalonResponse

from .rpg.db import Character, Clan, Party


class Diagnostics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coolio = []

    @commands.command(aliases=("harakiri",))
    @bot.owner_only
    async def seppuku(self, ctx: commands.Context):
        """
        Kills the bot.
        """
        await HanalonEmbed(title="さよなら〜", context=ctx).respond(True, override=True)
        await self.bot.change_presence(status=discord.Status.invisible)
        await self.bot.close()

    @commands.command()
    async def echo(self, ctx: commands.Context, *, msg: str):
        """
        Echoes a message in the specified channel (if given). Defaults to same channel.
        """
        guild = ctx.guild
        channel = ctx.channel
        if len(words := msg.split()) > 1:
            if match := re.match(r"^<#([0-9]+)>$", words[0]):
                channel_id = int(match.group(1))
                if guild:
                    channel = guild.get_channel(channel_id)
                    msg = " ".join(words[1:])
        await HanalonEmbed(description=msg, context=ctx).respond(
            True, destination=channel
        )

    # @commands.command()
    # async def test(self, ctx: commands.Context):
    #     if self.coolio == []:
    #         await bot.characters.delete_many(dict())
    #         await bot.parties.delete_many(dict())
    #         await bot.clans.delete_many(dict())
    #     a = await Character.register(ctx.author, "Enira", "Assassin", "Dhampir")
    #     b = await Character.register(ctx.author, "Phoria", "Mage", "Faerie")
    #     c = await Character.register(ctx.author, "Nara", "Spellsword", "Catfolk")
    #     d = await Character.register(ctx.author, "Nocta", "Artificer", "Elf")
    #     e = await Character.register(ctx.author, "Næia", "Ranger", "Birdfolk")
    #     f = await Character.register(ctx.author, "Qwillia", "Paladin", "Amazon")
    #     x = await Party.register(ctx.author, [a, b, c, d, e, f])
    #     for n in await x.get_characters():
    #         await ctx.send(f'{await n.get_name()}\n{await n.get_jobs_dict()}\n{await n.get_race()}\n{await n.get_xp()}')
    #     self.coolio += [ctx.author]
    #
    # @commands.command()
    # @bot.owner_only
    # async def test2(self, ctx: commands.Context):
    #     v = await Clan.register(ctx.author, "Mechranox")
    #     for n in self.coolio:
    #         try:
    #             await v.add_member(n)
    #         except:
    #             ...
    #     members = await v.get_members()
    #     members = [await x.get_player() for x in members]
    #     l = await v.get_leader()
    #     l = await l.get_player()
    #     await ctx.send(f'{[x.name for x in members]}\n{await v.get_name()}\n{l.name}')
    #


def setup(bot):
    include_cog(bot, Diagnostics)
