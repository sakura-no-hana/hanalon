from datetime import datetime, timezone
import logging
import pathlib
import sys

from utils.bot import run

if __name__ == "__main__":
    if sys.argv[-1] == "docker":
        log_file = pathlib.Path(f"logs/{datetime.now(timezone.utc).isoformat()}.log")
    else:
        log_file = pathlib.Path(f"../logs/{datetime.now(timezone.utc).isoformat()}.log")

    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename=log_file, encoding="utf-8", mode="w+")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)

    run()
