import asyncio
from datetime import datetime
import logging

import motor.motor_asyncio

from utils.bot import config

log = motor.motor_asyncio.AsyncIOMotorClient(config["mongo"])["log"]["bot"]


class MongoLog(logging.Handler):
    def emit(self, record):
        asyncio.ensure_future(
            log.insert_one(
                {
                    "time": datetime.now(),
                    "level": record.levelname,
                    "message": record.msg % record.args,
                }
            )
        )
