from typing import List, Tuple
from functools import lru_cache
import onnxruntime
from imgutils.data import load_image, rgb_encode
import os

from ..hf_downloader import HFDownloader
from .yolo_ import _image_preprocess, _data_postprocess
from .plot import detection_visualize

class HeadDetector:
    _HEAD_MODELS = ['head_detect_v0_s']
    _DEFAULT_HEAD_MODEL = _HEAD_MODELS[0]
    _LABELS = ['head']

    def __init__(self, max_infer_size=640, conf_threshold=0.45, iou_threshold=0.7):
        self.max_infer_size = max_infer_size
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

    @lru_cache()
    def _open_head_detect_model(self):
        model_path = f'./module/model/{self._HEAD_MODELS[0]}.onnx'
        if not os.path.exists(model_path):
            HFDownloader().download_model(f'{self._HEAD_MODELS[0]}.onnx')
        return onnxruntime.InferenceSession(model_path)

    def detect_heads(self, image_path: str, model_name: str = _DEFAULT_HEAD_MODEL) -> List[Tuple[Tuple[int, int, int, int], str, float]]:
        image = load_image(image_path, mode='RGB')
        new_image, old_size, new_size = _image_preprocess(image, self.max_infer_size)
        data = rgb_encode(new_image)[None, ...]
        output, = self._open_head_detect_model().run(['output0'], {'images': data})
        return _data_postprocess(output[0], self.conf_threshold, self.iou_threshold, old_size, new_size, self._LABELS)

    def get_head_coordinate(self, image_path: str, model_name: str = _DEFAULT_HEAD_MODEL):
        ret = self.detect_heads(image_path, model_name)
        return detection_visualize(image_path, ret, self._LABELS)
