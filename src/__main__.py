import logging
import os
import sys

import setproctitle

from utils.discord.bot import run
from utils.log import MongoLog

if __name__ == "__main__":
    dname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dname)
    sys.path.insert(1, dname)

    setproctitle.setproctitle("hanalon-bot")

    logging.getLogger("discord").addHandler(MongoLog("bot", logging.DEBUG))

    if "pod_name" in os.environ:
        run(int(os.environ["pod_name"].split("-")[-1]), int(os.environ["shard_count"]))
    else:
        run(-1, 1)
