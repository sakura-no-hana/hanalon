from discord.ext import commands


class Items(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send("Hello, world!")


def setup(bot):
    bot.add_cog(Items(bot))
