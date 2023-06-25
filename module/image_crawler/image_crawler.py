from ..config import DOWNLOAD_CONFIG
from .crawlers.users_crawler import UserCrawler
from .utils import checkDir


class ImageCrawler:
    def __init__(self, artist_id, capacity=200):
        checkDir(DOWNLOAD_CONFIG["STORE_PATH"])
        self.artist_id = artist_id
        self.capacity = capacity
        self.crawler = UserCrawler(artist_id, capacity)

    def run(self):
        return self.crawler.run()
