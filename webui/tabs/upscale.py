"""Image upscaling (Real-ESRGAN) tab component."""

import logging
import os
import tempfile
from typing import List, Optional

import cv2
import gradio as gr
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_scaler = None


def _get_scaler():
    global _scaler
    if _scaler is None:
        from module.image_scaler.image_scaler import _get_upscaler

        logger.info("Loading Real-ESRGAN model (first use may download ~17 MB)...")
        _get_upscaler()
        _scaler = True
    from module.image_scaler.image_scaler import _get_upscaler

    return _get_upscaler()


def _process(
    images: Optional[List[str]],
    scale: float,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not images:
        gr.Warning("请先上传图片")
        return []

    upscaler = _get_scaler()

    results: List[str] = []
    for i, img_path in enumerate(images):
        progress((i + 1) / len(images), desc=f"正在放大 {i + 1}/{len(images)}")

        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue

        output, _ = upscaler.enhance(img, outscale=scale)

        pil = Image.fromarray(
            cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
            if len(output.shape) == 3 and output.shape[2] == 3
            else output
        )

        tmp = tempfile.mkdtemp()
        base = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(tmp, f"{base}_upscaled.png")
        pil.save(out_path, format="PNG")
        results.append(out_path)

    gr.Info(f"完成！已放大 {len(results)} 张图片（{scale}×）")
    return results


def create_tab() -> None:
    """Build the image-upscale tab inside a ``gr.Tab`` context."""
    with gr.Tab("图片放大"):
        gr.Markdown(
            "使用 Real-ESRGAN 对图片进行超分辨率放大（4× 动漫专用模型）。"
            "适合提升裁剪后低分辨率图片的画质。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传图片",
                    file_types=["image"],
                    file_count="multiple",
                )
                scale_slider = gr.Slider(
                    1.0,
                    8.0,
                    value=4.0,
                    step=0.5,
                    label="放大倍数",
                    info="模型原生 4×，其他倍数通过插值实现",
                )
                run_btn = gr.Button("开始放大", variant="primary", size="lg")
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="放大结果",
                    columns=2,
                    height="auto",
                    object_fit="contain",
                )
        run_btn.click(
            _process,
            inputs=[file_input, scale_slider],
            outputs=gallery,
        )
