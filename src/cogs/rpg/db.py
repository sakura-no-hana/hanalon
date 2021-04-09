from enum import Enum, unique
import math
from typing import Iterable, Optional, Union
from uuid import uuid4 as uuid

import bson
import discord

from utils.bot import bot


class RPGException(Exception):
    ...


class AlreadyRegistered(RPGException):
    ...


class NotRegistered(RPGException):
    ...


@unique
class Job(Enum):
    ROGUE = 0
    BARD = 1
    ASSASSIN = 2
    RANGER = 3
    ALCHEMIST = 4
    ARTIFICER = 5
    ADVENTURER = 6
    DRUID = 7
    MONK = 8
    MAGE = 9
    WARLOCK = 10
    CLERIC = 11
    SPELLSWORD = 12
    PALADIN = 13
    KNIGHT = 14
    WARRIOR = 15


@unique
class Race(Enum):
    HUMAN = 0
    ELF = 1
    DWARF = 2
    FAERIE = 3
    GNOME = 4
    HALFLING = 5
    CATFOLK = 6
    DOGFOLK = 7
    BIRDFOLK = 8
    RABBITFOLK = 9
    LIZARDFOLK = 10
    SIREN = 11
    AMAZON = 12
    TIEFLING = 13
    ORC = 14
    DHAMPIR = 15


@unique
class Damage(Enum):
    ACID = 0
    BLUDGEONING = 1
    COLD = 2
    FIRE = 3
    FORCE = 4
    LIGHTNING = 5
    NECROTIC = 6
    PIERCING = 7
    POISON = 8
    PSYCHIC = 9
    RADIANT = 10
    SLASHING = 11
    THUNDER = 12


class Character:
    @classmethod
    async def register(
        cls, player: discord.User, name: str, job: str, race: Optional[str] = "human"
    ):
        if job.upper() not in [c.name for c in list(Job)] or race.upper() not in [
            r.name for r in list(Race)
        ]:
            raise ValueError
        jobs = [0] * 16
        jobs[Job[job.upper()].value] = 1
        await bot.characters.insert_one(
            {
                "_id": (id := uuid()),
                "player": bson.Int64(player.id),
                "name": name,
                "jobs": jobs,
                "race": Race[race.upper()].value,
                "xp": 0,
            }
        )
        return cls(id)

    def __init__(self, identifier):
        self.identifier = identifier

    async def get_name(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return _["name"]

    # no name setter since I don't see the demand + it's trivial for later implementation

    async def get_race(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return Race(_["race"]).name

    # same thing with race

    async def get_xp(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return _["xp"]

    async def set_xp(self, new):
        if not await bot.characters.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.characters.update_one({"_id": self.identifier}, {"$set": {"xp": new}})

    async def inc_xp(self, inc):
        if not await bot.characters.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.characters.update_one({"_id": self.identifier}, {"$inc": {"xp": inc}})

    async def get_level(self):
        xp = await self.get_xp()
        return math.ceil(math.log(xp/5 + math.e))

    async def get_jobs(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return _["jobs"]

    async def get_jobs_dict(self):
        jobs = await self.get_jobs()
        job_dict = dict()
        for i, job in enumerate(jobs):
            job_dict[Job(i).name] = job
        return job_dict

    async def set_jobs(self, new):
        if not await bot.characters.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.characters.update_one(
            {"_id": self.identifier}, {"$set": {"jobs": new}}
        )

    async def set_jobs_dict(self, new):
        if not await bot.characters.find_one({"_id": self.identifier}):
            raise NotRegistered
        jobs = [0] * 16
        for k, v in new.items():
            jobs[Job(k)] = v
        await bot.characters.update_one(
            {"_id": self.identifier}, {"$set": {"jobs": jobs}}
        )

    async def get_player(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return await bot.fetch_user(_["player"])


class Party:
    @classmethod
    async def register(
        cls, player: discord.User, characters: Optional[Iterable[Character]] = []
    ):
        exists = await bot.parties.find_one({"player": bson.Int64(player.id)})
        if exists:
            raise AlreadyRegistered
        await bot.parties.insert_one(
            {
                "_id": (id := uuid()),
                "player": bson.Int64(player.id),
                "characters": [c.identifier for c in characters],
            }
        )
        return cls(id)

    @classmethod
    async def from_user(cls, user: discord.User):
        _ = await bot.parties.find_one({"player": bson.Int64(user.id)})
        if not _:
            raise NotRegistered
        return cls(_["_id"])

    def __init__(self, identifier):
        self.identifier = identifier

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
        _ = await bot.parties.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return [Character(identifier) for identifier in _["characters"]]

    async def set_characters(self, new):
        if not await bot.parties.find_one({"_id": self.identifier}):
            raise NotRegistered
        await bot.parties.update_one(
            {"_id": self.identifier},
            {"$set": {"characters": [c.identifier for c in new]}},
        )

    async def get_player(self):
        _ = await bot.parties.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return await bot.fetch_user(_["player"])


Player = Union[discord.User, discord.Member, Party]


class Clan:
    @classmethod
    async def register(cls, player: Player, name: str):
        exists = await bot.clans.find_one({"members": bson.Int64(player.id)})
        if exists:
            raise AlreadyRegistered
        if isinstance(player, discord.User) or isinstance(player, discord.Member):
            player = await Party.from_user(player)
        await bot.clans.insert_one(
            {
                "_id": (id := uuid()),
                "leader": player.identifier,
                "name": name,
                "members": [player.identifier],
            }
        )
        return cls(id)

    @classmethod
    async def from_user(cls, user: Player):
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = await Party.from_user(user)
        _ = await bot.clans.find_one({"members": user.identifier})
        if not _:
            raise NotRegistered
        return cls(_["_id"])

    def __init__(self, identifier):
        self.identifier = identifier

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

    @classmethod
    async def rem_member(self, user: Player):
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = await Party.from_user(user)
        c = await Clan.from_user(user)
        await bot.clans.update_one(
            {"_id": c.identifier}, {"$pull": {"members": user.identifier}}
        )

    async def get_members(self):
        _ = await bot.clans.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return [Party(identifier) for identifier in _["members"]]

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
        _ = await bot.clans.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return _["name"]

    async def get_leader(self):
        _ = await bot.clans.find_one({"_id": self.identifier})
        if not _:
            raise NotRegistered
        return Party(_["leader"])

    async def set_leader(self, user: Player):
        if not await bot.clans.find_one({"_id": self.identifier}):
            raise NotRegistered
        if isinstance(user, discord.User) or isinstance(user, discord.Member):
            user = Party.from_user(user)
        await bot.clans.update_one(
            {"_id": self.identifier}, {"$set": {"leader": user.identifier}}
        )


def setup(bot):
    bot.characters = bot.db["character"]
    bot.parties = bot.db["party"]
    bot.clans = bot.db["clan"]
    bot.shop = bot.db["shop"]
