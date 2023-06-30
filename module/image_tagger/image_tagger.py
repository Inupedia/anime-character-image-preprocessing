import os
import re
import cv2
import numpy as np
import pandas as pd
from PIL import Image
from onnxruntime import InferenceSession
from typing import Mapping, Tuple, Dict
from tqdm import tqdm
from ..config import IMAGE_CONFIG
import os


class ImageTagger:
    def __init__(
        self,
        model_path="./module/model/model.onnx",
        tags_path="./module/model/selected_tags.csv",
        image_directory="./src/input",
        image_files=None,
    ) -> None:
        self.image_directory = IMAGE_CONFIG["IMAGE_TAGGER_INPUT_DIR"]
        self.__model_path = model_path
        self.__tags_path = tags_path
        self.__initialized = False
        self._model, self._tags = None, None
        if image_files is None:
            self.image_files = [
                filename
                for filename in os.listdir(image_directory)
                if filename.endswith((".jpg", ".png", ".jpeg"))
            ]
        else:
            self.image_files = image_files

    def _init(self) -> None:
        if self.__initialized:
            return
        self._model = InferenceSession(str(self.__model_path))
        self._tags = pd.read_csv(self.__tags_path)
        self.__initialized = True

    # noinspection PyUnresolvedReferences
    def make_square(self, img, target_size):
        old_size = img.shape[:2]
        desired_size = max(old_size)
        desired_size = max(desired_size, target_size)

        delta_w = desired_size - old_size[1]
        delta_h = desired_size - old_size[0]
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        color = [255, 255, 255]
        return cv2.copyMakeBorder(
            img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
        )

    # noinspection PyUnresolvedReferences
    def smart_resize(self, img, size):
        # Assumes the image has already gone through make_square
        if img.shape[0] > size:
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        elif img.shape[0] < size:
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_CUBIC)
        else:  # just do nothing
            pass

        return img

    def _calculation(self, image: Image.Image) -> pd.DataFrame:
        self._init()

        _, height, _, _ = self._model.get_inputs()[0].shape
        image = image.convert("RGBA")
        new_image = Image.new("RGBA", image.size, "WHITE")
        new_image.paste(image, mask=image)
        image = new_image.convert("RGB")
        image = np.asarray(image)
        image = image[:, :, ::-1]
        image = self.make_square(image, height)
        image = self.smart_resize(image, height)
        image = image.astype(np.float32)
        image = np.expand_dims(image, 0)

        input_name = self._model.get_inputs()[0].name
        label_name = self._model.get_outputs()[0].name
        confidence = self._model.run([label_name], {input_name: image})[0]

        full_tags = self._tags[["name", "category"]].copy()
        full_tags["confidence"] = confidence[0]

        return full_tags

    def interrogate(self, image: Image) -> Tuple[Dict[str, float], Dict[str, float]]:
        full_tags = self._calculation(image)
        ratings = dict(
            full_tags[full_tags["category"] == 9][["name", "confidence"]].values
        )
        tags = dict(
            full_tags[full_tags["category"] != 9][["name", "confidence"]].values
        )
        return ratings, tags

    def tag_image(
        self,
        image: Image.Image,
        threshold: float,
        use_spaces: bool,
        use_escape: bool,
        include_ranks: bool,
        score_descend: bool,
    ) -> Tuple[Mapping[str, float], str, Mapping[str, float]]:
        ratings, tags = self.interrogate(image)

        filtered_tags = {
            tag: score for tag, score in tags.items() if score >= threshold
        }

        text_items = []
        tags_pairs = filtered_tags.items()

        if score_descend:
            tags_pairs = sorted(tags_pairs, key=lambda x: (-x[1], x[0]))
        for tag, score in tags_pairs:
            tag_outformat = tag
            if use_spaces:
                tag_outformat = tag_outformat.replace("_", " ")
            if use_escape:
                RE_SPECIAL = re.compile(r"([\\()])")
                tag_outformat = re.sub(RE_SPECIAL, r"\\\1", tag_outformat)
            text_items.append(tag_outformat)
        output_text = ", ".join(text_items)

        return ratings, output_text, filtered_tags

    def process_directory(
        self,
        confidence=IMAGE_CONFIG["IMAGE_TAGGER_CONFIDENCE"],
        use_spaces=True,
        use_escape=True,
        include_ranks=False,
        score_descend=True,
    ):
        for filename in tqdm(self.image_files, desc="Processing images"):
            image_path = os.path.join(self.image_directory, filename)
            image = Image.open(image_path)
            ratings, output_text, filtered_tags = self.tag_image(
                image,
                confidence,
                use_spaces,
                use_escape,
                include_ranks,
                score_descend,
            )
            # Write output text to a file with the same name as the image, but with .txt extension
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(self.image_directory, output_filename)
            with open(output_path, "w") as f:
                f.write(output_text)
