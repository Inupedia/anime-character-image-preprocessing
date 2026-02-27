"""Image tagging tab component."""

import logging
from typing import Optional, Tuple

import gradio as gr
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

_tagger_instance = None


def _get_tagger():
    global _tagger_instance
    if _tagger_instance is None:
        from module.image_tagger import ImageTagger

        logger.info("Loading tagger model (first use may download ~50 MB)...")
        _tagger_instance = ImageTagger()
    return _tagger_instance


def _process(
    image: Optional[np.ndarray], confidence: float
) -> Tuple[str, str]:
    if image is None:
        gr.Warning("请先上传图片")
        return "", ""

    tagger = _get_tagger()
    pil_img = Image.fromarray(image)
    ratings, tag_text, _ = tagger.tag_image(pil_img, confidence)

    ratings_str = "\n".join(
        f"{k}: {v:.4f}"
        for k, v in sorted(ratings.items(), key=lambda x: -x[1])
    )

    gr.Info("标签生成完成")
    return tag_text, ratings_str


def create_tab() -> None:
    """Build the image-tagging tab inside a ``gr.Tab`` context."""
    with gr.Tab("图片标注"):
        gr.Markdown(
            "使用 WD Tagger 自动生成 Booru 风格标签，"
            "可直接用于 Stable Diffusion 训练。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(label="上传图片", type="numpy")
                conf_slider = gr.Slider(
                    0.1,
                    1.0,
                    value=0.5,
                    step=0.05,
                    label="置信度阈值",
                    info="越高越精确，但可能遗漏部分标签",
                )
                run_btn = gr.Button("生成标签", variant="primary", size="lg")
            with gr.Column(scale=1):
                tags_box = gr.Textbox(
                    label="标签（逗号分隔，可直接复制使用）",
                    lines=8,
                )
                ratings_box = gr.Textbox(label="分类评级", lines=4)
        run_btn.click(
            _process,
            inputs=[image_input, conf_slider],
            outputs=[tags_box, ratings_box],
        )
