import logging
import os
from typing import Callable, List, Tuple

import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm

from ..config import IMAGE_CONFIG
from ..image_processor.image_processor import list_image_files
from .face_detector import FaceDetector

logger = logging.getLogger(__name__)


class SmartCropper:
    def __init__(self, cascade_file: str = "lbpcascade_animeface.xml", scale: float = 1.0):
        cascade_path = os.path.join(os.path.dirname(__file__), cascade_file)
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.scale = scale
        self.face_detector = FaceDetector()

    def calculate_crop_coordinates(
        self,
        face_x: int,
        face_y: int,
        face_width: int,
        face_height: int,
        image_width: int,
        image_height: int,
    ) -> Tuple[int, int, int, int]:
        face_center_x = face_x + face_width // 2
        face_center_y = face_y + face_height // 2
        distance = max(face_width, face_height) * self.scale

        top = max(0, int(face_center_y - distance))
        bottom = min(image_height, int(face_center_y + distance))
        left = max(0, int(face_center_x - distance))
        right = min(image_width, int(face_center_x + distance))

        return left, top, right - left, bottom - top

    def _process_and_save_image(
        self, image_path: str, process_func: Callable[[np.ndarray, Tuple[int, ...]], np.ndarray]
    ) -> None:
        image = cv2.imread(image_path)
        if image is None:
            logger.warning("Cannot read image: %s", image_path)
            return

        faces = list(self.face_detector.get_face_coordinate(image_path))
        if not faces:
            logger.warning("No faces detected in: %s", image_path)
            return

        for idx, face in enumerate(faces):
            processed_image = process_func(image, face)
            filename, ext = os.path.splitext(os.path.basename(image_path))
            output_path = os.path.join(
                IMAGE_CONFIG["SMART_CROP_OUTPUT_DIR"],
                f"{filename}_smart_crop_{idx}{ext}",
            )
            cv2.imwrite(output_path, processed_image)

    def face_image_process(self, image: np.ndarray, face: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, x2, y2 = face
        return image[y:y2, x:x2]

    def smart_image_process(self, image: np.ndarray, face: Tuple[int, int, int, int]) -> np.ndarray:
        x, y, x2, y2 = face
        image_height, image_width = image.shape[:2]
        left, top, width, height = self.calculate_crop_coordinates(
            x, y, x2 - x, y2 - y, image_width, image_height
        )
        return image[top: top + height, left: left + width]

    def smart_image_process_fast(self, image: np.ndarray, face: Tuple[int, int, int, int]) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        if len(faces) > 0:
            x, y, w, h = faces[0]
            image_height, image_width = image.shape[:2]
            crop_x, crop_y, crop_width, crop_height = self.calculate_crop_coordinates(
                x, y, w, h, image_width, image_height
            )
            return image[crop_y: crop_y + crop_height, crop_x: crop_x + crop_width]
        logger.warning("No faces detected by cascade classifier, returning original image.")
        return image

    def crop_and_save_all(self, process_func: Callable) -> None:
        image_directory = IMAGE_CONFIG["SMART_CROP_INPUT_DIR"]
        image_files = list_image_files(image_directory)
        for filename in tqdm(image_files, desc="Processing images"):
            self._process_and_save_image(os.path.join(image_directory, filename), process_func)
