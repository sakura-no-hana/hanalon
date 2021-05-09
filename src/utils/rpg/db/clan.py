from dataclasses import dataclass
from typing import Iterable, Union
from uuid import UUID
from uuid import uuid4 as uuid

import bson
import discord

from utils.discord.bot import bot
from utils.rpg.db.exceptions import AlreadyRegistered, NotRegistered
from utils.rpg.db.party import Party

Player = Union[discord.User, discord.Member, Party]


@dataclass
class Clan:
    identifier: UUID

    @classmethod
    async def register(cls, player: Player, name: str):
        exists = await bot.clans.find_one({"members": bson.Int64(player.id)})
        duplicate_name = await bot.clans.find_one({"name": name})
        if exists or duplicate_name:
            raise AlreadyRegistered
        if isinstance(player, discord.User) or isinstance(player, discord.Member):
            player = await Party.from_user(player)
        await bot.clans.insert_one(
            {
                "_id": (identifier := uuid()),
                "leader": player.identifier,
                "name": name,
                "members": [player.identifier],
            }
        )
        return cls(identifier)

    @classmethod
    async def from_user(cls, user: Player):
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = await Party.from_user(user)
        if not (clan := await bot.clans.find_one({"members": user.identifier})):
            raise NotRegistered
        return cls(clan["_id"])

    async def add_member(self, user: Player):
        try:
            await Clan.from_user(user)
            raise AlreadyRegistered
        except NotRegistered:
            if not await bot.clans.find_one({"_id": self.identifier}):
                raise NotRegistered
            if isinstance(user, discord.User) or isinstance(user, discord.Member):
                user = await Party.from_user(user)
            await bot.clans.update_one(
                {"_id": self.identifier}, {"$push": {"members": user.identifier}}
            )

    # might as well use a class method, since there's only one possible clan a user can be in

    @staticmethod
    async def rem_member(user: Player):
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = await Party.from_user(user)
        c = await Clan.from_user(user)
        await bot.clans.update_one(
            {"_id": c.identifier}, {"$pull": {"members": user.identifier}}
        )

    async def get_members(self):
        if not (clan := await bot.clans.find_one({"_id": self.identifier})):
            raise NotRegistered
        return [Party(identifier) for identifier in clan["members"]]

    async def set_members(self, new: Iterable[Player]):
        if not await bot.clans.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.clans.update_one(
            {"_id": self.identifier},
            {
                "$set": {
                    "characters": [
                        c.identifier
                        if isinstance(c, Party)
                        else await Party.from_user(c)
                        for c in new
                    ]
                }
            },
        )

    async def get_name(self):
        if not (clan := await bot.clans.find_one({"_id": self.identifier})):
            raise NotRegistered
        return clan["name"]

    async def get_leader(self):
        if not (clan := await bot.clans.find_one({"_id": self.identifier})):
            raise NotRegistered
        return Party(clan["leader"])

    async def set_leader(self, user: Player):
        if not await bot.clans.find_one({"_id": self.identifier}):
            raise NotRegistered
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = Party.from_user(user)
        await bot.clans.update_one(
            {"_id": self.identifier}, {"$set": {"leader": user.identifier}}
        )
