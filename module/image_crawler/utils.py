import logging
import os
from functools import wraps
from threading import Lock
from typing import Callable

log_lock = Lock()
logger = logging.getLogger(__name__)


def writeFailLog(text: str) -> None:
    with log_lock:
        with open("fail_log.txt", "a+") as f:
            f.write(text)


def timeLog(func: Callable) -> Callable:
    @wraps(func)
    def clocked(*args, **kwargs):
        from time import time
        start_time = time()
        ret = func(*args, **kwargs)
        logger.info("%s() finished in %.2f s", func.__name__, time() - start_time)
        return ret
    return clocked


def printInfo(msg: str) -> None:
    logger.info(msg)


def printWarn(expr: bool, msg: object) -> None:
    if expr:
        logger.warning(str(msg))


def printError(expr: bool, msg: str) -> None:
    if expr:
        logger.error(msg)
        raise RuntimeError(msg)


def checkDir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info("Created directory: %s", dir_path)
