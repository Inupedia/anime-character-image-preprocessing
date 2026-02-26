import concurrent.futures as futures
import logging
import urllib.parse as urlparse
from typing import Set

from tqdm import tqdm

from ..collector.collector import Collector
from ..collector.collector_unit import collect
from ..collector.selectors import selectKeyword
from ...config import DOWNLOAD_CONFIG, USER_CONFIG, IMAGE_CONFIG
from ..downloader.downloader import Downloader

logger = logging.getLogger(__name__)


class KeywordCrawler:
    """Download Pixiv search results for a keyword."""

    def __init__(self, keyword: str, capacity: int = 1024):
        self.keyword = keyword
        self.order = IMAGE_CONFIG.KEYWORD_ORDER
        self.mode = IMAGE_CONFIG.KEYWORD_MODE
        self.n_page = IMAGE_CONFIG.KEYWORD_N_PAGES
        self.downloader = Downloader(capacity)
        self.collector = Collector(self.downloader)

    def collect(self) -> None:
        logger.info("Start collecting keyword: %s", self.keyword)

        url_template = (
            "https://www.pixiv.net/ajax/search/artworks/"
            + "{}?word={}".format(
                urlparse.quote(self.keyword, safe="()"), urlparse.quote(self.keyword)
            )
            + "&order={}".format("popular_d" if self.order else "date_d")
            + f"&mode={self.mode}"
            + "&p={}&s_mode=s_tag&type=all&lang=zh"
        )
        urls: Set[str] = {url_template.format(i + 1) for i in range(self.n_page)}

        n_thread = DOWNLOAD_CONFIG.N_THREAD
        with futures.ThreadPoolExecutor(n_thread) as executor:
            with tqdm(total=len(urls), desc="collecting ids") as pbar:
                additional_headers = {"Cookie": USER_CONFIG.COOKIE}
                for image_ids in executor.map(
                    collect,
                    zip(
                        urls,
                        [selectKeyword] * len(urls),
                        [additional_headers] * len(urls),
                    ),
                ):
                    if image_ids is not None:
                        self.collector.add(image_ids)
                    pbar.update()

        logger.info("Collection complete for keyword: %s", self.keyword)
        logger.info("Downloadable artworks: %d", len(self.collector.id_group))

    def run(self) -> float:
        self.collect()
        self.collector.collect()
        return self.downloader.download()
