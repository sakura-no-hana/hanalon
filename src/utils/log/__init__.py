import asyncio
from datetime import datetime
import logging

import motor.motor_asyncio

from utils.discord.bot import config


class MongoLog(logging.Handler):
    def __init__(self, loc, level):
        super().__init__(level=level)
        self.log = motor.motor_asyncio.AsyncIOMotorClient(config["mongo"])["log"][loc]

    def emit(self, record):
        asyncio.ensure_future(
            self.log.insert_one(
                {
                    "time": datetime.now(),
                    "level": record.levelname,
                    "message": record.msg % record.args,
                }
            )
        )
