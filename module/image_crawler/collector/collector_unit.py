import logging
import time
from typing import Callable, Dict, Iterable, Optional, Tuple

import requests

from ...config import DOWNLOAD_CONFIG, NETWORK_CONFIG
from ..utils import writeFailLog

logger = logging.getLogger(__name__)


def collect(args: Tuple[str, Callable, Optional[Dict]]) -> Optional[Iterable[str]]:
    """Generic metadata collector using pluggable selector functions.

    Args:
        args: Tuple of (url, selector_function, additional_headers).
    """
    url, selector, additional_headers = args
    headers = {**NETWORK_CONFIG.HEADER}
    if additional_headers is not None:
        headers.update(additional_headers)

    logger.debug("Collecting %s", url)
    time.sleep(DOWNLOAD_CONFIG.THREAD_DELAY)

    for attempt in range(DOWNLOAD_CONFIG.N_TIMES):
        try:
            response = requests.get(
                url, headers=headers, proxies=NETWORK_CONFIG.PROXY, timeout=4
            )
            if response.status_code == 200:
                logger.debug("Collected %s", url)
                return selector(response)

        except Exception as e:
            logger.debug("Attempt %d to collect %s: %s", attempt + 1, url, e)
            time.sleep(DOWNLOAD_CONFIG.FAIL_DELAY)

    logger.warning("Failed to collect %s", url)
    writeFailLog(f"fail to collect {url}\n")
    return None
