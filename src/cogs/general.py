import discord
from discord.ext import commands

from utils.access import is_dev
from utils.responses import HanalonEmbed, HanalonResponse


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, precision='4'):
        await HanalonEmbed(title='🏓 Pong!',
                           description=f'{("%." + precision + "f") % self.bot.latency} seconds!',
                           message=ctx.message).respond(True)

    @commands.group()
    async def about(self, ctx):
        if ctx.invoked_subcommand is None:
            e = HanalonEmbed(ctx.message, title='About me',
                             description="Hello! I'm Hanalon, your friendly Adventurers' Guild receptionist! Don't hesitate to consult me if you need anything!")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.add_field(name='Version', value="I'm still in my infancy… teehee~!", inline=False)
            e.add_field(name='Library', value="I'm a homunculus made with discord.py!",
                        inline=False)
            devs = [await self.bot.fetch_user(dev) for dev in self.bot.devs]
            e.add_field(name='Developers', value='I loyally serve my masters: ' + ' and '.join(
                [f'{dev.name}#{dev.discriminator}' for dev in devs]), inline=False)
            e.add_field(name='Servers',
                        value=f'I proudly serve {len(self.bot.guilds)} Guild branches!',
                        inline=False)
            e.add_field(name='Users',
                        value=f'I am the receptionist for {len(self.bot.users)} parties!',
                        inline=False)
            await e.respond(True)

    @about.command()
    async def party(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.message.author
        await ctx.send(user.name)

    @about.command()
    async def guild(self, ctx):
        await ctx.send(ctx.message.guild.name)


def setup(bot):
    bot.add_cog(General(bot))
