from dataclasses import dataclass
from enum import IntEnum
import math
import textwrap
from typing import Iterable, Optional
from uuid import UUID
from uuid import uuid4 as uuid

import bson
import discord

from utils.discord.bot import bot
from utils.rpg.db.exceptions import NotRegistered

Job = IntEnum(
    "Job",
    [
        "ROGUE",
        "BARD",
        "ASSASSIN",
        "RANGER",
        "ALCHEMIST",
        "ARTIFICER",
        "ADVENTURER",
        "DRUID",
        "MONK",
        "MAGE",
        "WARLOCK",
        "CLERIC",
        "SPELLSWORD",
        "PALADIN",
        "KNIGHT",
        "WARRIOR",
    ],
    start=0,
)

Race = IntEnum(
    "Race",
    [
        "HUMAN",
        "ELF",
        "DWARF",
        "FAERIE",
        "GNOME",
        "HALFLING",
        "CATFOLK",
        "DOGFOLK",
        "BIRDFOLK",
        "RABBITFOLK",
        "DRAGONBORN",
        "SIREN",
        "AMAZON",
        "TIEFLING",
        "ORC",
        "DHAMPIR",
    ],
    start=0,
)


Stats = IntEnum(
    "Stats",
    [
        "XP",
        "HP",
        "MAX_HP",
        "ARMOR",
        "SPEED",
        "STRENGTH",
        "DEXTERITY",
        "CONSTITUTION",
        "INTELLIGENCE",
        "WISDOM",
        "CHARISMA",
        "LUCK",
        "ACROBATICS",
        "ANIMAL_HANDLING",
        "ARCANA",
        "ATHLETICS",
        "DECEPTION",
        "HISTORY",
        "INSIGHT",
        "INTIMIDATION",
        "INVESTIGATION",
        "MEDICINE",
        "NATURE",
        "PERCEPTION",
        "PERFORMANCE",
        "PERSUATION",
        "RELIGION",
        "SLEIGHT_OF_HAND",
        "STEALTH",
        "SURVIVAL",
    ],
    start=0,
)

# TODO: create race and class classes to handle stat matrix modifications


@dataclass
class Character:
    identifier: UUID

    @classmethod
    async def gen_stats(cls, job: dict[Race, int], race: int, core: Iterable[int]):
        """This should be used to generate stats."""
        s = [0] * 30

        s[Stats.STRENGTH : Stats.LUCK + 1] = core[:7]
        s[Stats.ATHLETICS] = s[Stats.STRENGTH]
        s[Stats.ACROBATICS] = s[Stats.SLEIGHT_OF_HAND] = s[Stats.STEALTH] = s[
            Stats.DEXTERITY
        ]
        s[Stats.ARCANA] = s[Stats.HISTORY] = s[Stats.INVESTIGATION] = s[
            Stats.NATURE
        ] = s[Stats.RELIGION] = s[Stats.INTELLIGENCE]
        s[Stats.ANIMAL_HANDLING] = s[Stats.INSIGHT] = s[Stats.MEDICINE] = s[
            Stats.PERCEPTION
        ] = s[Stats.SURVIVAL] = s[Stats.WISDOM]
        s[Stats.DECEPTION] = s[Stats.INTIMIDATION] = s[Stats.PERFORMANCE] = s[
            Stats.PERSUASION
        ] = s[Stats.CHARISMA]

        # TODO: apply racial and class modifiers here

        return s

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

        # TODO: use `gen_stats` here

        await bot.characters.insert_one(
            {
                "_id": (identifier := uuid()),
                "player": bson.Int64(player.id),
                "name": name,
                "jobs": jobs,
                "race": Race[race.upper()].value,
                "stats": [0] * 30,
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

    for stat in Stats:
        get_query = "{'_id': self.identifier}, {'_id': 0, 'stats': 1}"
        set_query = "{'_id': self.identifier}, {'$set': {'stats.%s': new}}" % stat.value

        exec(
            textwrap.dedent(
                f"""
                async def get_{stat.name.lower()}(self):
                    if not (char := await bot.characters.find_one({get_query})):
                        raise NotRegistered
                    return char["stats"][{stat.value}]
                
                async def set_{stat.name.lower()}(self, new):
                    if not await bot.characters.find_one({get_query}):
                        raise NotRegistered
                    await bot.characters.update_one({set_query})
                """
            )
        )

    # TODO: make a better level algorithm

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
        return bot.get_user(char["player"]) or (await bot.fetch_user(char["player"]))
