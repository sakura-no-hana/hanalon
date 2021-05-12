from typing import Iterable, Optional
from uuid import uuid4 as uuid

import bson
import discord

from utils.discord.bot import bot
from utils.rpg.db.base import BaseData
from utils.rpg.db.character import Character
from utils.rpg.db.exceptions import AlreadyRegistered, NotRegistered


class Party(BaseData):
    @classmethod
    async def register(
        cls, player: discord.User, characters: Optional[Iterable[Character]] = tuple()
    ):
        exists = await bot.parties.find_one({"player": bson.Int64(player.id)})
        if exists:
            raise AlreadyRegistered
        await bot.parties.insert_one(
            {
                "_id": (identifier := uuid()),
                "player": bson.Int64(player.id),
                "characters": [c.identifier for c in characters],
            }
        )
        return cls(identifier)

    @classmethod
    async def from_user(cls, user: discord.User):
        if not (party := await bot.parties.find_one({"player": bson.Int64(user.id)})):
            raise NotRegistered
        return cls(party["_id"])

    async def add_character(self, char: Character):
        if not await bot.parties.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.parties.update_one(
            {"_id": self.identifier}, {"$push": {"characters": char.identifier}}
        )

    async def rem_character(self, char: Character):
        await bot.clans.update_one(
            {"_id": self.identifier}, {"$pull": {"characters": char.identifier}}
        )

    async def get_characters(self):
        if not (party := await bot.parties.find_one({"_id": self.identifier})):
            raise NotRegistered
        return [Character(identifier) for identifier in party["characters"]]

    async def set_characters(self, new):
        if not await bot.parties.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.parties.update_one(
            {"_id": self.identifier},
            {"$set": {"characters": [c.identifier for c in new]}},
        )

    async def get_player(self):
        if not (party := await bot.parties.find_one({"_id": self.identifier})):
            raise NotRegistered
        return bot.get_user(party["player"]) or (await bot.fetch_user(party["player"]))
