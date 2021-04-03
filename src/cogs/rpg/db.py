from enum import Enum, unique
import math
from typing import Iterable, Optional
from uuid import uuid4 as uuid

import bson
import discord

from utils.bot import bot


class RPGException(Exception):
    ...


class AlreadyRegistered(RPGException):
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
        return _["name"]

    # no name setter since I don't see the demand + it's trivial for later implementation

    async def get_race(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        return Race(_["race"]).name

    # same thing with race

    async def get_xp(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        return _["xp"]

    async def set_xp(self, new):
        await bot.characters.update_one({"_id": self.identifier}, {"$set": {"xp": new}})

    async def inc_xp(self, inc):
        await bot.characters.update_one({"_id": self.identifier}, {"$inc": {"xp": inc}})

    async def get_level(self):
        xp = await self.get_xp()
        return math.ceil(math.log(xp + math.e))

    async def get_jobs(self):
        _ = await bot.characters.find_one({"_id": self.identifier})
        return _["jobs"]

    async def get_jobs_dict(self):
        jobs = await self.get_jobs()
        job_dict = dict()
        for i, job in enumerate(jobs):
            job_dict[Job(i).name] = job
        return job_dict

    async def set_jobs(self, new):
        await bot.characters.update_one(
            {"_id": self.identifier}, {"$set": {"jobs": new}}
        )

    async def set_jobs_dict(self, new):
        jobs = [0] * 16
        for k, v in new.items():
            jobs[Job(k)] = v
        await bot.characters.update_one(
            {"_id": self.identifier}, {"$set": {"jobs": jobs}}
        )


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
        return bot.parties.find_one({"player": bson.Int64(user.id)})

    def __init__(self, identifier):
        self.identifier = identifier

    async def get_characters(self):
        _ = await bot.parties.find_one({"_id": self.identifier})
        return [Character(identifier) for identifier in _["characters"]]

    async def set_characters(self, new):
        await bot.parties.update_one(
            {"_id": self.identifier},
            {"$set": {"characters": [c.identifier for c in new]}},
        )


def setup(bot):
    bot.characters = bot.db["character"]
    bot.parties = bot.db["party"]
    bot.clans = bot.db["clan"]
    bot.shop = bot.db["shop"]
