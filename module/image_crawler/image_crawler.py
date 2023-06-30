from ..config import DOWNLOAD_CONFIG
from .crawlers import *
from .utils import checkDir


class ImageCrawlerFactory:
    _crawlers = {"User": UserCrawler, "Keyword": KeywordCrawler}

    @staticmethod
    def create_crawler(crawler_type, keyword_or_id, capacity=200):
        print(keyword_or_id)
        if crawler_type in ImageCrawlerFactory._crawlers:
            return ImageCrawlerFactory._crawlers[crawler_type](keyword_or_id, capacity)
        else:
            raise ValueError(f"Invalid crawler_type: {crawler_type}")


class ImageCrawler:
    def __init__(self, crawler_type, keyword_or_id, capacity=200):
        checkDir(DOWNLOAD_CONFIG["STORE_PATH"])
        self.crawler = ImageCrawlerFactory.create_crawler(
            crawler_type, keyword_or_id[0], capacity
        )

    def run(self):
        return self.crawler.run()
