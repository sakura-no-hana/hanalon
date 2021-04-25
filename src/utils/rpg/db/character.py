from dataclasses import dataclass
from enum import Enum, unique
import math
from typing import Optional
from uuid import UUID
from uuid import uuid4 as uuid

import bson
import discord

from utils.discord.bot import bot
from utils.rpg.db.exceptions import NotRegistered


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
    BLADESINGER = 12
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
    DRAGONBORN = 10
    SIREN = 11
    AMAZON = 12
    TIEFLING = 13
    ORC = 14
    DHAMPIR = 15


@dataclass
class Character:
    identifier: UUID

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
                "_id": (identifier := uuid()),
                "player": bson.Int64(player.id),
                "name": name,
                "jobs": jobs,
                "race": Race[race.upper()].value,
                "xp": 0,
            }
        )
        return cls(identifier)

    async def get_name(self):
        if not (char := await bot.characters.find_one({"_id": self.identifier})):
            raise NotRegistered
        return char["name"]

    # no name setter since I don't see the demand + it's trivial for later implementation

    async def get_race(self):
        if not (char := await bot.characters.find_one({"_id": self.identifier})):
            raise NotRegistered
        return Race(char["race"]).name

    # same thing with race

    async def get_xp(self):
        if not (char := await bot.characters.find_one({"_id": self.identifier})):
            raise NotRegistered
        return char["xp"]

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
        return math.ceil(math.log(xp / 5 + math.e))

    async def get_jobs(self):
        if not (char := await bot.characters.find_one({"_id": self.identifier})):
            raise NotRegistered
        return char["jobs"]

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
        if not (char := await bot.characters.find_one({"_id": self.identifier})):
            raise NotRegistered
        return await bot.fetch_user(char["player"])
