from functools import lru_cache
from typing import List, Tuple

from huggingface_hub import hf_hub_download
from imgutils.data import ImageTyping, load_image, rgb_encode

from onnx_ import _open_onnx_model
from plot import detection_visualize
from yolo_ import _image_preprocess, _data_postprocess

import onnxruntime

_HEAD_MODELS = [
    'head_detect_v0_s',
]

_DEFAULT_HEAD_MODEL = _HEAD_MODELS[0]


@lru_cache()
def _open_head_detect_model(model_name):
    return onnxruntime.InferenceSession(f'./model/{model_name}.onnx')


_LABELS = ['head']


def detect_heads(image: ImageTyping, model_name: str, max_infer_size=640,
                 conf_threshold: float = 0.45, iou_threshold: float = 0.7) \
        -> List[Tuple[Tuple[int, int, int, int], str, float]]:
    image = load_image(image, mode='RGB')
    new_image, old_size, new_size = _image_preprocess(image, max_infer_size)

    data = rgb_encode(new_image)[None, ...]
    output, = _open_head_detect_model(model_name).run(['output0'], {'images': data})
    return _data_postprocess(output[0], conf_threshold, iou_threshold, old_size, new_size, _LABELS)


def _gr_detect_heads(image: ImageTyping, model_name: str, max_infer_size=640,
                     conf_threshold: float = 0.45, iou_threshold: float = 0.7):
    ret = detect_heads(image, model_name, max_infer_size, conf_threshold, iou_threshold)
    return detection_visualize(image, ret, _LABELS)
