"""Crawler utility functions."""

import logging
import os
from threading import Lock

log_lock = Lock()
logger = logging.getLogger(__name__)


def writeFailLog(text: str) -> None:
    """Append a failure message to fail_log.txt (thread-safe)."""
    with log_lock:
        with open("fail_log.txt", "a+") as f:
            f.write(text)


def checkDir(dir_path: str) -> None:
    """Create directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logger.info("Created directory: %s", dir_path)
