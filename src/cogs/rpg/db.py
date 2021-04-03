from enum import Enum, unique
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
class Class(Enum):
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
    def register(
        cls, player: discord.User, name: str, job: str, race: Optional[str] = "human"
    ):
        if job.upper() not in [c.name for c in list(Class)] or race.upper() not in [
            r.name for r in list(Race)
        ]:
            raise ValueError
        bot.characters.insert_one(
            {
                "identifier": uuid(),
                "owner": bson.Int64(player.id),
                "name": name,
                "job": Class[job.upper()],
                "race": Race[race.upper()],
            }
        )


class Party:
    @classmethod
    def register(
        cls, player: discord.User, characters: Optional[Iterable[Character]] = []
    ):
        if bot.parties.find_one({"identifier": bson.Int64(player.id)}):
            raise AlreadyRegistered
        bot.parties.insert_one(
            {
                "identifier": bson.Int64(player.id),
                "characters": [c.id for c in characters],
            }
        )


def setup(bot):
    bot.characters = bot.db["character"]
    bot.parties = bot.db["party"]
    bot.clans = bot.db["clan"]
    bot.shop = bot.db["shop"]
