from datetime import datetime, timezone
import logging

import pymongo

from utils.bot import config, run

collection = pymongo.MongoClient(config["mongo"])["log"]["bot"]


class MongoLog(logging.Handler):
    def emit(self, entry):
        collection.insert_one(
            {"time": datetime.now(), "level": entry.levelname, "message": entry.msg}
        )


if __name__ == "__main__":

    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)

    logger.addHandler(MongoLog(logging.DEBUG))

    run()
