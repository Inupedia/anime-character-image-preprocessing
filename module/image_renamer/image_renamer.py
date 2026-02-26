import logging
import os
from typing import List

from PIL import Image

from ..config import IMAGE_CONFIG

logger = logging.getLogger(__name__)


class ImageRenamer:
    def __init__(self, folder_path: str = "./src/input"):
        self.folder_path = folder_path
        self.image_files: List[str] = self._get_image_files()

    def _get_image_files(self) -> List[str]:
        image_files: List[str] = []
        for filename in sorted(os.listdir(self.folder_path)):
            filepath = os.path.join(self.folder_path, filename)
            if not os.path.isfile(filepath):
                continue
            try:
                with Image.open(filepath) as img:
                    img.verify()
                image_files.append(filename)
            except (IOError, SyntaxError):
                pass
        return image_files

    def rename_files(self) -> None:
        prefix = IMAGE_CONFIG["IMAGE_PREFIX"]
        for idx, filename in enumerate(self.image_files):
            _, ext = os.path.splitext(filename)
            new_name = f"{prefix}_{idx}{ext}"
            old_path = os.path.join(self.folder_path, filename)
            new_path = os.path.join(self.folder_path, new_name)
            if old_path != new_path:
                os.rename(old_path, new_path)
                logger.debug("Renamed %s → %s", filename, new_name)

    def run(self) -> None:
        self.rename_files()
        logger.info("Renamed %d files with prefix '%s'", len(self.image_files), IMAGE_CONFIG["IMAGE_PREFIX"])
