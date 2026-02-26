import logging
import os
from functools import lru_cache
from typing import List, Tuple

import onnxruntime
from imgutils.data import load_image, rgb_encode

from ..hf_downloader import HFDownloader
from .plot import extract_face_boundaries
from .yolo_ import _image_preprocess, _data_postprocess

logger = logging.getLogger(__name__)


class FaceDetector:
    _FACE_MODELS = ["face_detect_v1.4_s"]
    _DEFAULT_FACE_MODEL = _FACE_MODELS[0]
    _LABELS = ["face"]

    def __init__(
        self,
        max_infer_size: int = 500,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.7,
    ):
        self.max_infer_size = max_infer_size
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    @lru_cache()
    def _open_face_detect_model(self) -> onnxruntime.InferenceSession:
        model_path = f"./module/model/{self._FACE_MODELS[0]}.onnx"
        if not os.path.exists(model_path):
            HFDownloader().download_model(f"{self._FACE_MODELS[0]}.onnx")
        return onnxruntime.InferenceSession(model_path)

    def detect_faces(
        self, image_path: str, model_name: str = _DEFAULT_FACE_MODEL
    ) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        image = load_image(image_path, mode="RGB")
        new_image, old_size, new_size = _image_preprocess(image, self.max_infer_size)
        data = rgb_encode(new_image)[None, ...]
        (output,) = self._open_face_detect_model().run(["output0"], {"images": data})
        return _data_postprocess(
            output[0], self.conf_threshold, self.iou_threshold, old_size, new_size, self._LABELS
        )

    def get_face_coordinate(
        self, image_path: str, model_name: str = _DEFAULT_FACE_MODEL
    ) -> List[Tuple[int, int, int, int]]:
        detections = self.detect_faces(image_path, model_name)
        return extract_face_boundaries(image_path, detections, self._LABELS)