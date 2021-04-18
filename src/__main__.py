import logging
import os

from utils.bot import run
from utils.log import MongoLog

if __name__ == "__main__":
    logging.getLogger("discord").addHandler(MongoLog(logging.DEBUG))

    if "pod_name" in os.environ:
        run(int(os.environ["pod_name"].split("-")[-1]), int(os.environ["shard_count"]))
    else:
        run(-1, 1)
