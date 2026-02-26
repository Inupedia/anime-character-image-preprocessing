import logging
import os
import re
import time

import requests

from ...config import DOWNLOAD_CONFIG, NETWORK_CONFIG
from ..utils import writeFailLog

logger = logging.getLogger(__name__)

_IMAGE_ID_PATTERN = re.compile(r"/(\d+)_")


class ImageDownloader:
    def download_image(self, url: str) -> float:
        """Download a single image from Pixiv.

        Returns:
            Image size in MB, or 0 on failure/skip.
        """
        image_name = url[url.rfind("/") + 1:]
        match = _IMAGE_ID_PATTERN.search(url)
        if match is None:
            logger.error("Bad URL format (cannot extract image ID): %s", url)
            return 0

        image_id = match.group(1)
        headers = {
            "Referer": f"https://www.pixiv.net/artworks/{image_id}",
            **NETWORK_CONFIG.HEADER,
        }

        logger.debug("Downloading %s", image_name)
        time.sleep(DOWNLOAD_CONFIG.THREAD_DELAY)

        image_path = os.path.join(DOWNLOAD_CONFIG.STORE_PATH, image_name)
        if os.path.exists(image_path):
            logger.debug("File already exists: %s", image_path)
            return 0

        wait_time = 10
        for attempt in range(DOWNLOAD_CONFIG.N_TIMES):
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    proxies=NETWORK_CONFIG.PROXY,
                    timeout=(4, wait_time),
                )

                if response.status_code == 200:
                    content_length = int(response.headers.get("content-length", 0))
                    if content_length and len(response.content) != content_length:
                        time.sleep(DOWNLOAD_CONFIG.FAIL_DELAY)
                        wait_time += 2
                        continue

                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    logger.debug("Downloaded %s", image_name)
                    return len(response.content) / (1 << 20)

            except Exception as e:
                logger.debug("Attempt %d to download %s: %s", attempt + 1, image_name, e)
                time.sleep(DOWNLOAD_CONFIG.FAIL_DELAY)

        logger.warning("Failed to download %s after %d attempts", image_name, DOWNLOAD_CONFIG.N_TIMES)
        writeFailLog(f"fail to download {image_name}\n")
        return 0
