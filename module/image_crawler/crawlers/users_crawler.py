import logging

from ..collector.collector import Collector
from ..collector.collector_unit import collect
from ..collector.selectors import selectUser
from ...config import USER_CONFIG
from ..downloader.downloader import Downloader

logger = logging.getLogger(__name__)


class UserCrawler:
    """Collect all artworks from a single Pixiv artist.

    URL format: https://www.pixiv.net/ajax/user/{artist_id}/profile/all?lang=zh
    """

    def __init__(self, artist_id: str, capacity: int = 1024):
        self.artist_id = artist_id
        self.downloader = Downloader(capacity)
        self.collector = Collector(self.downloader)

    def collect(self) -> None:
        logger.info("Collecting artworks for user %s", self.artist_id)
        url = f"https://www.pixiv.net/ajax/user/{self.artist_id}/profile/all?lang=zh"
        additional_headers = {
            "Referer": f"https://www.pixiv.net/users/{self.artist_id}/illustrations",
            "x-user-id": USER_CONFIG["USER_ID"],
            "Cookie": USER_CONFIG["COOKIE"],
        }
        image_ids = collect((url, selectUser, additional_headers))
        if image_ids is not None:
            self.collector.add(image_ids)
        logger.info("Collection complete for user %s", self.artist_id)

    def run(self) -> float:
        self.collect()
        self.collector.collect()
        return self.downloader.download()
