import discord
from discord.ext import commands, slash

from utils.bot import include_cog
from utils.responses import HanalonEmbed, HanalonResponse


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, precision: int = 4):
        await HanalonEmbed(title='🏓 Pong!',
                           description=f'{("%." + str(precision) + "f") % self.bot.latency} seconds!',
                           context=ctx).respond(True)

    @slash.cmd(name='ping')
    async def _ping(self, ctx: slash.Context,
                    precision: slash.Option(description='precision', required=False,
                                            type=slash.ApplicationCommandOptionType.INTEGER) = 4):
        '''Returns the ping to a specified precision (default is to nearest 10⁻⁴ seconds)'''
        await HanalonEmbed(title='🏓 Pong!',
                           description=f'{("%." + str(precision) + "f") % self.bot.latency} seconds!',
                           context=ctx).respond()

    @commands.group()
    async def about(self, ctx):
        if ctx.invoked_subcommand is None:
            e = HanalonEmbed(ctx, title='About me',
                             description="Hello! I'm Hanalon, your friendly Adventurers' Guild receptionist! Don't hesitate to consult me if you need anything!")
            e.set_thumbnail(url=self.bot.user.avatar_url)
            e.add_field(name='Version', value="I'm still in my infancy… teehee~!", inline=False)
            e.add_field(name='Library', value="I'm a homunculus made with discord.py!",
                        inline=False)
            devs = [await self.bot.fetch_user(dev) for dev in self.bot.devs]
            e.add_field(name='Developers', value='I loyally serve my masters: ' + ', '.join(
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
    include_cog(bot, General)
