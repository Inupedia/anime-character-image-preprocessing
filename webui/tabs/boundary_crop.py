"""Boundary crop tab component."""

import logging
import os
import tempfile
from typing import List, Optional

import cv2
import gradio as gr
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def _process(
    images: Optional[List[str]],
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not images:
        gr.Warning("请先上传图片")
        return []

    results: List[str] = []
    for i, img_path in enumerate(images):
        progress((i + 1) / len(images), desc=f"正在裁剪 {i + 1}/{len(images)}")
        img = Image.open(img_path)
        arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        gray = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            h, w = arr.shape[:2]
            x, y, bw, bh = 0, 0, w, h
        else:
            boxes = [cv2.boundingRect(c) for c in contours]
            x = min(b[0] for b in boxes)
            y = min(b[1] for b in boxes)
            bw = max(b[0] + b[2] for b in boxes) - x
            bh = max(b[1] + b[3] for b in boxes) - y

        cropped = img.crop((x, y, x + bw, y + bh))

        tmp = tempfile.mkdtemp()
        base = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(tmp, f"{base}_crop.png")
        cropped.save(out_path, format="PNG")
        results.append(out_path)

    gr.Info(f"完成！已裁剪 {len(results)} 张图片")
    return results


def create_tab() -> None:
    """Build the boundary-crop tab inside a ``gr.Tab`` context."""
    with gr.Tab("边界裁剪"):
        gr.Markdown(
            "自动检测角色边界并裁剪掉多余空白。"
            "建议先用「背景去除」处理后再使用本功能，效果更佳。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传图片",
                    file_types=["image"],
                    file_count="multiple",
                )
                run_btn = gr.Button("开始裁剪", variant="primary", size="lg")
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="裁剪结果",
                    columns=3,
                    height="auto",
                    object_fit="contain",
                )
        run_btn.click(_process, inputs=[file_input], outputs=gallery)
