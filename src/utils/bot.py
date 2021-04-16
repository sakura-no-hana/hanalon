import base64
import logging
import os
import pathlib
from typing import Set, Union

import discord
from discord.ext import commands, slash
from motor.motor_asyncio import AsyncIOMotorClient
import yaml

Context = Union[commands.Context, slash.Context]
Bot = Union[commands.Bot, slash.SlashBot]

config_file = pathlib.Path("../config.yaml")

if "config" in os.environ:
    config = yaml.load(
        base64.b64decode(os.environ["config"]).decode("utf-8"), Loader=yaml.CSafeLoader
    )
else:
    try:
        with open(config_file, encoding="utf-8") as file:
            config = yaml.load(file, Loader=yaml.CSafeLoader)
    except FileNotFoundError:
        logging.critical("No configuration found; bot cannot start.")
        raise


def prefix(bot: Bot, message: discord.Message) -> Set[str]:
    """Returns the set of prefixes the bot accepts."""
    return {"$", f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "}


intents = discord.Intents.none()
intents.guilds = True
intents.members = True
intents.messages = True
intents.reactions = True

bot = commands.AutoShardedBot(
    command_prefix=prefix,
    intents=intents,
    debug_guild=config["guild"],
    owner_ids=config["devs"],
)
bot.color = config["color"]
bot.success = config["success"]
bot.failure = config["failure"]
bot.db = AsyncIOMotorClient(config["mongo"])["hanalon"]
cogs_dir = pathlib.Path("./cogs")

bot.owner_only = commands.check(lambda ctx: bot.is_owner(ctx.author))


def include_cog(cog: commands.Cog):
    """Loads a cog."""
    bot.add_cog(cog())
    # bot.add_slash_cog(cog())


def load_cogs():
    """Loads all cogs."""
    for root, _, files in os.walk(cogs_dir):
        for f in files:
            if (module := cogs_dir / f).suffix == ".py":
                bot.load_extension(
                    f"{'.'.join(pathlib.Path(root).parts)}.{module.stem}"
                )


def is_response(ctx, message, response):
    try:
        return (
            message.reference.message_id == response.reply.id
            and message.author == ctx.author
        )
    except AttributeError:
        return False


@bot.listen("on_ready")
async def prepare():
    """Prepares the bot; it currently changes its presence."""
    print(f"Logged on as {bot.user.name}#{bot.user.discriminator}")
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(
            name="the Sola bot arena", type=discord.ActivityType.competing
        ),
    )


@bot.listen("on_command_error")
async def handle(ctx: Context, error: commands.CommandError):
    """Handles command errors; it currently reacts to them."""
    if not isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction(bot.failure)
    raise error


def run(shard_id, shard_total):
    """Starts the bot."""
    load_cogs()
    if shard_id != -1:
        bot.shard_count = shard_total
        bot.shard_ids = [shard_id]
    bot.run(config["token"])
