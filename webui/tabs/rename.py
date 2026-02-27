"""Batch rename tab component."""

import os
import shutil
import tempfile
from typing import List, Optional

import gradio as gr


def _process(
    images: Optional[List[str]], prefix: str
) -> Optional[List[str]]:
    if not images:
        gr.Warning("请先上传图片")
        return None

    prefix = prefix.strip() or "illust"
    tmp = tempfile.mkdtemp()
    paths: List[str] = []
    for idx, path in enumerate(images):
        ext = os.path.splitext(path)[1]
        new_name = f"{prefix}_{idx}{ext}"
        dst = os.path.join(tmp, new_name)
        shutil.copy2(path, dst)
        paths.append(dst)

    gr.Info(f"完成！已重命名 {len(paths)} 张图片（前缀: {prefix}）")
    return paths


def create_tab() -> None:
    """Build the batch-rename tab inside a ``gr.Tab`` context."""
    with gr.Tab("批量重命名"):
        gr.Markdown(
            "将上传的图片按顺序编号重命名"
            "（如 `illust_0.jpg`, `illust_1.jpg`, …）。"
        )
        with gr.Row():
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传图片",
                    file_types=["image"],
                    file_count="multiple",
                )
                prefix_box = gr.Textbox(
                    value="illust",
                    label="命名前缀",
                    placeholder="illust",
                )
                run_btn = gr.Button("重命名", variant="primary", size="lg")
            with gr.Column(scale=1):
                file_output = gr.File(
                    label="下载重命名后的图片",
                    file_count="multiple",
                )
        run_btn.click(
            _process,
            inputs=[file_input, prefix_box],
            outputs=file_output,
        )
