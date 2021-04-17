import asyncio
from datetime import datetime
import logging
import os

import motor.motor_asyncio

from utils.bot import config, run

collection = motor.motor_asyncio.AsyncIOMotorClient(config["mongo"])["log"]["bot"]


class MongoLog(logging.Handler):
    def emit(self, record):
        asyncio.ensure_future(
            collection.insert_one(
                {
                    "time": datetime.now(),
                    "level": record.levelname,
                    "message": record.msg % record.args,
                }
            )
        )


if __name__ == "__main__":
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)

    logger.addHandler(MongoLog(logging.DEBUG))

    if "pod_name" in os.environ:
        run(int(os.environ["pod_name"].split("-")[-1]), int(os.environ["shard_count"]))
    else:
        run(-1, 1)
