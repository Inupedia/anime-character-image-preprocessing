"""Pixiv image crawler tab component."""

import logging
import os
from typing import List, Optional

import gradio as gr

logger = logging.getLogger(__name__)


def _crawl_by_user(
    artist_id: Optional[str],
    capacity: int,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not artist_id or not artist_id.strip():
        gr.Warning("请输入画师 ID")
        return []

    from module.image_crawler import ImageCrawler

    progress(0, desc="正在抓取画师作品…")
    try:
        crawler = ImageCrawler("User", artist_id.strip(), int(capacity))
        total_mb = crawler.run()
    except Exception as e:
        gr.Warning(f"抓取失败: {e}")
        logger.exception("Pixiv user crawl failed")
        return []

    from module.config import DOWNLOAD_CONFIG

    store = DOWNLOAD_CONFIG.STORE_PATH
    files = _list_downloaded(store)
    gr.Info(f"完成！下载 {len(files)} 张图片（共 {total_mb:.1f} MB）")
    return files


def _crawl_by_keyword(
    keyword: Optional[str],
    capacity: int,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    if not keyword or not keyword.strip():
        gr.Warning("请输入搜索关键词")
        return []

    from module.image_crawler import ImageCrawler

    progress(0, desc="正在搜索并下载…")
    try:
        crawler = ImageCrawler("Keyword", keyword.strip(), int(capacity))
        total_mb = crawler.run()
    except Exception as e:
        gr.Warning(f"抓取失败: {e}")
        logger.exception("Pixiv keyword crawl failed")
        return []

    from module.config import DOWNLOAD_CONFIG

    store = DOWNLOAD_CONFIG.STORE_PATH
    files = _list_downloaded(store)
    gr.Info(f"完成！下载 {len(files)} 张图片（共 {total_mb:.1f} MB）")
    return files


def _list_downloaded(directory: str) -> List[str]:
    """Return paths to image files in *directory*."""
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    results: List[str] = []
    if not os.path.isdir(directory):
        return results
    for name in sorted(os.listdir(directory)):
        if os.path.splitext(name)[1].lower() in exts:
            results.append(os.path.join(directory, name))
    return results


def create_tab() -> None:
    """Build the Pixiv crawler tab inside a ``gr.Tab`` context."""
    with gr.Tab("Pixiv 下载"):
        gr.Markdown(
            "从 Pixiv 按画师 ID 或关键词下载图片。\n\n"
            "> **注意：** 需要在 `module/config.py` 中配置有效的 "
            "Pixiv Cookie 和 User ID，以及代理设置。"
        )

        with gr.Tabs():
            # ---------- By Artist ID ----------
            with gr.Tab("按画师 ID"):
                with gr.Row():
                    with gr.Column(scale=1):
                        user_id_input = gr.Textbox(
                            label="画师 ID",
                            placeholder="例如: 12345678",
                            info="可在画师主页 URL 中找到: pixiv.net/users/{ID}",
                        )
                        user_capacity = gr.Slider(
                            10,
                            500,
                            value=200,
                            step=10,
                            label="最大下载数量",
                        )
                        user_btn = gr.Button(
                            "开始下载", variant="primary", size="lg"
                        )
                    with gr.Column(scale=2):
                        user_gallery = gr.Gallery(
                            label="下载结果",
                            columns=4,
                            height="auto",
                            object_fit="contain",
                        )
                user_btn.click(
                    _crawl_by_user,
                    inputs=[user_id_input, user_capacity],
                    outputs=user_gallery,
                )

            # ---------- By Keyword ----------
            with gr.Tab("按关键词"):
                with gr.Row():
                    with gr.Column(scale=1):
                        keyword_input = gr.Textbox(
                            label="搜索关键词",
                            placeholder='例如: 初音ミク 或 "50000users AND hutao"',
                            info="PIXIV 会员可使用组合搜索语法",
                        )
                        kw_capacity = gr.Slider(
                            10,
                            500,
                            value=200,
                            step=10,
                            label="最大下载数量",
                        )
                        kw_btn = gr.Button(
                            "开始下载", variant="primary", size="lg"
                        )
                    with gr.Column(scale=2):
                        kw_gallery = gr.Gallery(
                            label="下载结果",
                            columns=4,
                            height="auto",
                            object_fit="contain",
                        )
                kw_btn.click(
                    _crawl_by_keyword,
                    inputs=[keyword_input, kw_capacity],
                    outputs=kw_gallery,
                )
