import concurrent.futures as futures
import logging
from typing import Iterable, Set

from tqdm import tqdm

from ...config import DOWNLOAD_CONFIG
from .download_image import ImageDownloader

logger = logging.getLogger(__name__)


class Downloader:
    """Threaded download controller with flow-size capacity limit."""

    def __init__(self, capacity: int):
        self.url_group: Set[str] = set()
        self.capacity = capacity
        self._image_downloader = ImageDownloader()

    def add(self, urls: Iterable[str]) -> None:
        for url in urls:
            self.url_group.add(url)

    def download(self) -> float:
        flow_size = 0.0
        logger.info("Downloader starting with %d URLs", len(self.url_group))

        n_thread = DOWNLOAD_CONFIG.N_THREAD
        with futures.ThreadPoolExecutor(n_thread) as executor:
            with tqdm(total=len(self.url_group), desc="downloading") as pbar:
                for image_size in executor.map(self._image_downloader.download_image, self.url_group):
                    flow_size += image_size
                    pbar.update()
                    pbar.set_description(f"downloading / flow {flow_size:.2f}MB")
                    if flow_size > self.capacity:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

        logger.info("Download complete. Total flow: %.2f MB", flow_size)
        return flow_size
