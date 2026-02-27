"""Smart crop (face-based) tab component."""

import logging
import os
import tempfile
from typing import List, Optional

import cv2
import gradio as gr
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_face_detector = None


def _get_face_detector():
    global _face_detector
    if _face_detector is None:
        from module.image_cropper.face_detector import FaceDetector

        logger.info("Loading face detector model...")
        _face_detector = FaceDetector()
    return _face_detector


def _process(
    images: Optional[List[str]],
    method: str,
    scale: float,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not images:
        gr.Warning("请先上传图片")
        return []

    from module.image_cropper.smart_cropper import SmartCropper

    cropper = SmartCropper(scale=scale)
    detector = _get_face_detector()

    results: List[str] = []
    for i, img_path in enumerate(images):
        progress((i + 1) / len(images), desc=f"正在智能裁剪 {i + 1}/{len(images)}")
        image = cv2.imread(img_path)
        if image is None:
            continue

        use_yolo = "YOLO" in method
        if use_yolo:
            faces = list(detector.get_face_coordinate(img_path))
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            det = cropper.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            faces = (
                [(x, y, x + w, y + h) for (x, y, w, h) in det]
                if len(det) > 0
                else []
            )

        if not faces:
            gr.Warning(
                f"图片 {os.path.basename(img_path)} 未检测到人脸，已跳过"
            )
            continue

        for fi, face in enumerate(faces):
            x, y, x2, y2 = face
            img_h, img_w = image.shape[:2]
            left, top, cw, ch = cropper.calculate_crop_coordinates(
                x, y, x2 - x, y2 - y, img_w, img_h
            )
            crop = image[top : top + ch, left : left + cw]
            pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))

            tmp = tempfile.mkdtemp()
            base = os.path.splitext(os.path.basename(img_path))[0]
            out_path = os.path.join(tmp, f"{base}_smartcrop_{fi}.png")
            pil.save(out_path, format="PNG")
            results.append(out_path)

    gr.Info(f"完成！共获得 {len(results)} 张裁剪图片")
    return results


def create_tab() -> None:
    """Build the smart-crop tab inside a ``gr.Tab`` context."""
    with gr.Tab("智能裁剪"):
        gr.Markdown(
            "基于人脸检测的智能裁剪。"
            "自动识别角色面部并按比例裁剪，支持多人图自动分割为多张。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传图片",
                    file_types=["image"],
                    file_count="multiple",
                )
                method_radio = gr.Radio(
                    choices=["auto (YOLO)", "auto-fast (Cascade)"],
                    value="auto (YOLO)",
                    label="检测方法",
                    info="YOLO 精度更高；Cascade 速度更快",
                )
                scale_slider = gr.Slider(
                    0.5,
                    3.0,
                    value=1.5,
                    step=0.1,
                    label="裁剪比例",
                    info="数值越大，保留面部周围区域越广",
                )
                run_btn = gr.Button("开始裁剪", variant="primary", size="lg")
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="裁剪结果",
                    columns=3,
                    height="auto",
                    object_fit="contain",
                )
        run_btn.click(
            _process,
            inputs=[file_input, method_radio, scale_slider],
            outputs=gallery,
        )
