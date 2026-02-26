import logging
import os
import re
from typing import Dict, List, Mapping, Optional, Tuple

import cv2
import numpy as np
import pandas as pd
from PIL import Image
from onnxruntime import InferenceSession
from tqdm import tqdm

from ..config import IMAGE_CONFIG
from ..hf_downloader import HFDownloader

logger = logging.getLogger(__name__)

_RE_SPECIAL = re.compile(r"([\\()])")


class ImageTagger:
    def __init__(
        self,
        model_path: str = "./module/model/model.onnx",
        tags_path: str = "./module/model/selected_tags.csv",
        image_files: Optional[List[str]] = None,
    ) -> None:
        self.image_directory: str = IMAGE_CONFIG["IMAGE_TAGGER_INPUT_DIR"]
        self._model_path = model_path
        self._tags_path = tags_path
        self._initialized = False
        self._model: Optional[InferenceSession] = None
        self._tags: Optional[pd.DataFrame] = None

        if image_files is None:
            self.image_files = [
                f for f in sorted(os.listdir(self.image_directory))
                if f.lower().endswith((".jpg", ".png", ".jpeg", ".webp", ".bmp"))
            ]
        else:
            self.image_files = image_files

    def _init(self) -> None:
        if self._initialized:
            return

        if not os.path.exists(self._model_path):
            HFDownloader().download_model(os.path.basename(self._model_path))

        if not os.path.exists(self._tags_path):
            HFDownloader().download_model(os.path.basename(self._tags_path))

        self._model = InferenceSession(str(self._model_path))
        self._tags = pd.read_csv(self._tags_path)
        self._initialized = True

    def _make_square(self, img: np.ndarray, target_size: int) -> np.ndarray:
        old_size = img.shape[:2]
        desired_size = max(max(old_size), target_size)

        delta_w = desired_size - old_size[1]
        delta_h = desired_size - old_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        return cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )

    def _smart_resize(self, img: np.ndarray, size: int) -> np.ndarray:
        if img.shape[0] > size:
            return cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        elif img.shape[0] < size:
            return cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
        return img

    def _calculation(self, image: Image.Image) -> pd.DataFrame:
        self._init()
        assert self._model is not None and self._tags is not None

        _, height, _, _ = self._model.get_inputs()[0].shape
        image = image.convert("RGBA")
        new_image = Image.new("RGBA", image.size, "WHITE")
        new_image.paste(image, mask=image)
        img_arr = np.asarray(new_image.convert("RGB"))
        img_arr = img_arr[:, :, ::-1]
        img_arr = self._make_square(img_arr, height)
        img_arr = self._smart_resize(img_arr, height)
        img_arr = img_arr.astype(np.float32)
        img_arr = np.expand_dims(img_arr, 0)

        input_name = self._model.get_inputs()[0].name
        label_name = self._model.get_outputs()[0].name
        confidence = self._model.run([label_name], {input_name: img_arr})[0]

        full_tags = self._tags[["name", "category"]].copy()
        full_tags["confidence"] = confidence[0]

        return full_tags

    def interrogate(self, image: Image.Image) -> Tuple[Dict[str, float], Dict[str, float]]:
        full_tags = self._calculation(image)
        ratings = dict(full_tags[full_tags["category"] == 9][["name", "confidence"]].values)
        tags = dict(full_tags[full_tags["category"] != 9][["name", "confidence"]].values)
        return ratings, tags

    def tag_image(
        self,
        image: Image.Image,
        threshold: float,
        use_spaces: bool = True,
        use_escape: bool = True,
        include_ranks: bool = False,
        score_descend: bool = True,
    ) -> Tuple[Mapping[str, float], str, Mapping[str, float]]:
        ratings, tags = self.interrogate(image)

        filtered_tags = {tag: score for tag, score in tags.items() if score >= threshold}

        tags_pairs = list(filtered_tags.items())
        if score_descend:
            tags_pairs = sorted(tags_pairs, key=lambda x: (-x[1], x[0]))

        text_items = []
        for tag, score in tags_pairs:
            tag_out = tag
            if use_spaces:
                tag_out = tag_out.replace("_", " ")
            if use_escape:
                tag_out = re.sub(_RE_SPECIAL, r"\\\1", tag_out)
            text_items.append(tag_out)

        return ratings, ", ".join(text_items), filtered_tags

    def process_directory(
        self,
        confidence: float = IMAGE_CONFIG["IMAGE_TAGGER_CONFIDENCE"],
        use_spaces: bool = True,
        use_escape: bool = True,
        include_ranks: bool = False,
        score_descend: bool = True,
    ) -> None:
        for filename in tqdm(self.image_files, desc="Processing images"):
            image_path = os.path.join(self.image_directory, filename)
            image = Image.open(image_path)
            _, output_text, _ = self.tag_image(
                image, confidence, use_spaces, use_escape, include_ranks, score_descend,
            )
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(self.image_directory, output_filename)
            with open(output_path, "w") as f:
                f.write(output_text)
