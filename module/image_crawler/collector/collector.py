import concurrent.futures as futures
import logging
from typing import Iterable, Set

from tqdm import tqdm

from ...config import DOWNLOAD_CONFIG, USER_CONFIG
from ..downloader import Downloader
from .collector_unit import collect
from .selectors import selectPage

logger = logging.getLogger(__name__)


class Collector:
    """Collect all image URLs in each artwork, and send to downloader.

    An artwork may contain multiple images.
    """

    def __init__(self, downloader: Downloader):
        self.id_group: Set[str] = set()
        self.downloader = downloader

    def add(self, image_ids: Iterable[str]) -> None:
        for image_id in image_ids:
            self.id_group.add(image_id)

    def collect(self) -> None:
        logger.info("Collector starting with %d artwork IDs", len(self.id_group))

        n_thread = DOWNLOAD_CONFIG.N_THREAD
        with futures.ThreadPoolExecutor(n_thread) as executor:
            with tqdm(total=len(self.id_group), desc="collecting urls") as pbar:
                page_urls = [
                    f"https://www.pixiv.net/ajax/illust/{illust_id}/pages?lang=zh"
                    for illust_id in self.id_group
                ]
                additional_headers = [
                    {
                        "Referer": f"https://www.pixiv.net/artworks/{illust_id}",
                        "x-user-id": USER_CONFIG.USER_ID,
                    }
                    for illust_id in self.id_group
                ]
                for image_urls in executor.map(
                    collect, zip(page_urls, [selectPage] * len(page_urls), additional_headers)
                ):
                    if image_urls is not None:
                        self.downloader.add(image_urls)
                    pbar.update()

        logger.info("Collector complete. Total images: %d", len(self.downloader.url_group))
