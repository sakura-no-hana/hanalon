import os
import pathlib
from typing import Set, Union

import discord
from discord.ext import commands, slash
import pymongo
import yaml

Context = Union[commands.Context, slash.Context]
Bot = Union[commands.Bot, slash.SlashBot]

with open("config.yaml") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


def prefix(bot: Bot, message: discord.Message) -> Set[str]:
    """
    Returns the set of prefixes the bot accepts
    """
    return {"$", f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "}


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = slash.SlashBot(
    command_prefix=prefix,
    intents=intents,
    debug_guild=config["guild"],
    owner_ids=config["devs"],
)
bot.color = config["color"]
bot.success = config["success"]
bot.failure = config["failure"]
bot.db = pymongo.MongoClient(config["mongo"])["hanalon"]
cogs_dir = pathlib.Path("./cogs")

bot.owner_only = commands.check(lambda ctx: bot.is_owner(ctx.author))


def include_cog(bot: Bot, cog: commands.Cog):
    """
    Loads a cog for both commands and slash
    """
    bot.add_cog(cog(bot))
    bot.add_slash_cog(cog(bot))


def load_cogs():
    """
    Loads all cogs
    """
    for root, dirs, files in os.walk(cogs_dir):
        for f in files:
            if (module := cogs_dir / f).suffix == ".py":
                bot.load_extension(f"{'.'.join(root.split('/'))}.{module.stem}")


@bot.listen("on_ready")
async def prepare():
    """
    Prepares the bot; it currently changes its presence
    """
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            name="the Sola bot arena", type=discord.ActivityType.competing
        ),
    )


@bot.listen("on_command_error")
async def handle(ctx: Context, error: commands.CommandError):
    """
    Handles command errors; it currently reacts to them
    """
    if not isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction(bot.failure)


def run():
    """
    Starts the bot
    """
    load_cogs()
    bot.run(config["token"])
