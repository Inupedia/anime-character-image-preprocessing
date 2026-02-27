"""Assembles all tab components into the main Gradio application."""

import gradio as gr

from .tabs import boundary_crop, remove_bg, rename, smart_crop, tagging

CSS = """
.header-row { text-align: center; margin-bottom: 0.5rem; }
"""


def build_app() -> gr.Blocks:
    """Create and return the Gradio ``Blocks`` application."""
    with gr.Blocks(title="Anime Image Preprocessing") as app:
        gr.Markdown(
            "# Anime Character Image Preprocessing\n"
            "动漫角色图片预处理工具 —— "
            "背景去除 · 边界裁剪 · 智能裁剪 · 图片标注 · 批量重命名",
            elem_classes="header-row",
        )

        with gr.Tabs():
            remove_bg.create_tab()
            boundary_crop.create_tab()
            smart_crop.create_tab()
            tagging.create_tab()
            rename.create_tab()

    return app
