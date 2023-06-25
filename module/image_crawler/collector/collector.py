import concurrent.futures as futures
import json
from typing import Dict, Iterable, List, Set

from ...config import DOWNLOAD_CONFIG, USER_CONFIG
from ..downloader.downloader import Downloader
from tqdm import tqdm
from ..utils import printInfo

from .collector_unit import collect
from .selectors import selectPage


class Collector:
    """[summary]
    collect all image ids in each artwork, and send to downloader
    NOTE: an artwork may contain multiple images
    """

    def __init__(self, downloader: Downloader):
        self.id_group: Set[str] = set()  # illust_id
        self.downloader = downloader

    def add(self, image_ids: Iterable[str]):
        for image_id in image_ids:
            self.id_group.add(image_id)

    def collect(self):
        """[summary]
        collect all image ids in each artwork, and send to downloader
        NOTE: an artwork may contain multiple images
        """

        printInfo("===== collector start =====")

        n_thread = DOWNLOAD_CONFIG["N_THREAD"]
        with futures.ThreadPoolExecutor(n_thread) as executor:
            with tqdm(total=len(self.id_group), desc="collecting urls") as pbar:
                urls = [
                    f"https://www.pixiv.net/ajax/illust/{illust_id}/pages?lang=zh"
                    for illust_id in self.id_group
                ]
                additional_headers = [
                    {
                        "Referer": f"https://www.pixiv.net/artworks/{illust_id}",
                        "x-user-id": USER_CONFIG["USER_ID"],
                    }
                    for illust_id in self.id_group
                ]
                for urls in executor.map(
                    collect, zip(urls, [selectPage] * len(urls), additional_headers)
                ):
                    if urls is not None:
                        self.downloader.add(urls)
                    pbar.update()

        printInfo("===== collector complete =====")
        printInfo(f"total images: {len(self.downloader.url_group)}")
