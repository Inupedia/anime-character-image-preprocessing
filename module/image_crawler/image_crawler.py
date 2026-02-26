import logging

from ..config import DOWNLOAD_CONFIG
from .crawlers import UserCrawler, KeywordCrawler
from .utils import checkDir

logger = logging.getLogger(__name__)

_CRAWLERS = {
    "User": UserCrawler,
    "Keyword": KeywordCrawler,
}


class ImageCrawler:
    def __init__(self, crawler_type: str, keyword_or_id: str, capacity: int = 200):
        checkDir(DOWNLOAD_CONFIG["STORE_PATH"])
        if crawler_type not in _CRAWLERS:
            raise ValueError(f"Invalid crawler_type: {crawler_type}")
        logger.info("Creating %s crawler for: %s", crawler_type, keyword_or_id)
        self.crawler = _CRAWLERS[crawler_type](keyword_or_id, capacity)

    def run(self) -> float:
        return self.crawler.run()
