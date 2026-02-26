import logging
import os
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

from ..config import IMAGE_CONFIG
from ..image_processor.image_processor import list_image_files

logger = logging.getLogger(__name__)


class BoundaryCropper:
    def __init__(self):
        self.image_directory = IMAGE_CONFIG["BOUNDARY_CROP_INPUT_DIR"]
        self.save_directory = IMAGE_CONFIG["BOUNDARY_CROP_OUTPUT_DIR"]
        os.makedirs(self.save_directory, exist_ok=True)
        self.image_files: List[str] = list_image_files(self.image_directory)

    def get_character_bounding_box(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            logger.warning("No contours found in image, returning full image bounds.")
            h, w = image.shape[:2]
            return 0, 0, w, h

        boxes = [cv2.boundingRect(c) for c in contours]
        x = min(b[0] for b in boxes)
        y = min(b[1] for b in boxes)
        w = max(b[0] + b[2] for b in boxes) - x
        h = max(b[1] + b[3] for b in boxes) - y

        return x, y, w, h

    def crop_and_save_all(self) -> None:
        for filename in tqdm(self.image_files, desc="Processing images"):
            image_path = os.path.join(self.image_directory, filename)
            img = Image.open(image_path)
            image_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            bbox = self.get_character_bounding_box(image_cv)
            if bbox is None:
                continue
            x, y, w, h = bbox
            cropped_img = img.crop((x, y, x + w, y + h))
            base_name, ext = os.path.splitext(os.path.basename(image_path))
            save_path = os.path.join(
                self.save_directory, f"{base_name}_boundary_crop{ext}"
            )
            cropped_img.save(save_path)
