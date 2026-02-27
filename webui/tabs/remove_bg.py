"""Background removal tab component."""

import io
import logging
import os
import tempfile
from typing import Dict, List, Optional

import gradio as gr
from PIL import Image

logger = logging.getLogger(__name__)

REMBG_MODELS = [
    "isnet-anime",
    "u2net",
    "u2netp",
    "u2net_human_seg",
    "u2net_cloth_seg",
    "silueta",
    "isnet-general-use",
]

_sessions: Dict[str, object] = {}


def _get_session(model_name: str):
    from rembg import new_session

    if model_name not in _sessions:
        logger.info("Loading rembg model: %s", model_name)
        _sessions[model_name] = new_session(model_name)
    return _sessions[model_name]


def _process(
    images: Optional[List[str]],
    model_name: str,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not images:
        gr.Warning("请先上传图片")
        return []

    from rembg import remove

    session = _get_session(model_name)

    results: List[str] = []
    for i, img_path in enumerate(images):
        progress((i + 1) / len(images), desc=f"正在处理 {i + 1}/{len(images)}")

        with open(img_path, "rb") as f:
            data = f.read()
        img = Image.open(io.BytesIO(data))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        out_data = remove(
            buf.getvalue(),
            session=session,
            post_process_mask=True,
            bgcolor=(255, 255, 255, 255),
        )
        out_img = Image.open(io.BytesIO(out_data))

        tmp = tempfile.mkdtemp()
        base = os.path.splitext(os.path.basename(img_path))[0]
        out_path = os.path.join(tmp, f"{base}_nobg.png")
        out_img.save(out_path, format="PNG")
        results.append(out_path)

    gr.Info(f"完成！已处理 {len(results)} 张图片")
    return results


def create_tab() -> None:
    """Build the background-removal tab inside a ``gr.Tab`` context."""
    with gr.Tab("背景去除"):
        gr.Markdown(
            "上传图片，自动去除背景并替换为白色。"
            "推荐使用 **isnet-anime** 模型处理动漫角色。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传图片",
                    file_types=["image"],
                    file_count="multiple",
                )
                model_dropdown = gr.Dropdown(
                    choices=REMBG_MODELS,
                    value="isnet-anime",
                    label="模型",
                    info="isnet-anime 专为动漫角色优化；u2net 更通用",
                )
                run_btn = gr.Button("开始处理", variant="primary", size="lg")
            with gr.Column(scale=2):
                gallery = gr.Gallery(
                    label="处理结果",
                    columns=3,
                    height="auto",
                    object_fit="contain",
                )
        run_btn.click(
            _process, inputs=[file_input, model_dropdown], outputs=gallery
        )
