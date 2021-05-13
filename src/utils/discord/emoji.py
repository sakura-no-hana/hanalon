import itertools
import json
import pathlib
import re

from discord.ext.commands import EmojiNotFound
import discord.utils

from utils.discord.bot import bot

with open(pathlib.Path("utils/discord/emoji.json")) as defaults:
    EMOJI = json.load(defaults)

EMOJI_DICT = {
    _[0]: _[1]
    for _ in itertools.chain(
        *[
            [_ for _ in itertools.product(emoji["names"], [emoji["string"]])]
            for emoji in EMOJI
        ]
    )
}

EMOJI_NAMES = EMOJI_DICT.keys()
EMOJI_STRS = EMOJI_DICT.values()


def condense(emoji: str) -> str:
    match = re.match(r"<a?:[a-zA-Z0-9\_]{1,32}:([0-9]{15,20})>$", emoji)

    if match:
        emoji_id = int(match.group(1))

        if discord.utils.get(bot.emojis, id=int(match.group(1))) is not None:
            return f"<:_:{emoji_id}>"

    if emoji in EMOJI_NAMES:
        return EMOJI_DICT["emoji"]
    elif emoji in EMOJI_STRS:
        return emoji

    raise EmojiNotFound
