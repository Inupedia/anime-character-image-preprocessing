"""Gradio web UI for the anime character image preprocessing tool.

Launch with::

    python app.py
"""

import io
import logging
import os
import shutil
import tempfile
from typing import Dict, List, Optional, Tuple

import cv2
import gradio as gr
import numpy as np
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
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

# ---------------------------------------------------------------------------
# Lazy-loaded singletons (heavy model loading only on first use)
# ---------------------------------------------------------------------------
_rembg_sessions: Dict[str, object] = {}
_tagger_instance = None
_face_detector = None


def _get_rembg_session(model_name: str):
    from rembg import new_session

    if model_name not in _rembg_sessions:
        logger.info("Loading rembg model: %s", model_name)
        _rembg_sessions[model_name] = new_session(model_name)
    return _rembg_sessions[model_name]


def _get_tagger():
    global _tagger_instance
    if _tagger_instance is None:
        from module.image_tagger import ImageTagger

        logger.info("Loading tagger model (first use may download ~50 MB)...")
        _tagger_instance = ImageTagger()
    return _tagger_instance


def _get_face_detector():
    global _face_detector
    if _face_detector is None:
        from module.image_cropper.face_detector import FaceDetector

        logger.info("Loading face detector model...")
        _face_detector = FaceDetector()
    return _face_detector


# ---------------------------------------------------------------------------
# Helper: save PIL images to temp files for gr.Gallery / gr.Files
# ---------------------------------------------------------------------------


def _save_temp(img: Image.Image, name: str, fmt: str = "PNG") -> str:
    tmp = tempfile.mkdtemp()
    ext = ".png" if fmt == "PNG" else ".jpg"
    path = os.path.join(tmp, f"{name}{ext}")
    img.save(path, format=fmt)
    return path


# ---------------------------------------------------------------------------
# Processing functions
# ---------------------------------------------------------------------------


def remove_bg(
    images: Optional[List[str]],
    model_name: str,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    """Remove background from uploaded images."""
    if not images:
        gr.Warning("请先上传图片")
        return []

    from rembg import remove

    session = _get_rembg_session(model_name)

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
        base = os.path.splitext(os.path.basename(img_path))[0]
        results.append(_save_temp(out_img, f"{base}_nobg"))

    gr.Info(f"完成！已处理 {len(results)} 张图片")
    return results


def boundary_crop(
    images: Optional[List[str]],
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    """Crop images to character boundaries."""
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
        base = os.path.splitext(os.path.basename(img_path))[0]
        results.append(_save_temp(cropped, f"{base}_crop"))

    gr.Info(f"完成！已裁剪 {len(results)} 张图片")
    return results


def smart_crop(
    images: Optional[List[str]],
    method: str,
    scale: float,
    progress: gr.Progress = gr.Progress(),
) -> List[str]:
    """Smart crop around detected faces."""
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
            gr.Warning(f"图片 {os.path.basename(img_path)} 未检测到人脸，已跳过")
            continue

        for fi, face in enumerate(faces):
            x, y, x2, y2 = face
            img_h, img_w = image.shape[:2]
            left, top, cw, ch = cropper.calculate_crop_coordinates(
                x, y, x2 - x, y2 - y, img_w, img_h
            )
            crop = image[top : top + ch, left : left + cw]
            pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            base = os.path.splitext(os.path.basename(img_path))[0]
            results.append(_save_temp(pil, f"{base}_smartcrop_{fi}"))

    gr.Info(f"完成！共获得 {len(results)} 张裁剪图片")
    return results


def tag_image(
    image: Optional[np.ndarray], confidence: float
) -> Tuple[str, str]:
    """Tag a single image and return (tags_text, ratings_text)."""
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


def rename_images(
    images: Optional[List[str]], prefix: str
) -> Optional[List[str]]:
    """Rename images with sequential prefix."""
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


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

CSS = """
.header-row { text-align: center; margin-bottom: 0.5rem; }
"""


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Anime Image Preprocessing") as app:
        gr.Markdown(
            "# Anime Character Image Preprocessing\n"
            "动漫角色图片预处理工具 — 背景去除 · 边界裁剪 · 智能裁剪 · 图片标注 · 批量重命名",
            elem_classes="header-row",
        )

        with gr.Tabs():
            # ==================== Background Removal ====================
            with gr.Tab("背景去除"):
                gr.Markdown(
                    "上传图片，自动去除背景并替换为白色。推荐使用 **isnet-anime** 模型处理动漫角色。"
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        bg_input = gr.File(
                            label="上传图片",
                            file_types=["image"],
                            file_count="multiple",
                        )
                        bg_model = gr.Dropdown(
                            choices=REMBG_MODELS,
                            value="isnet-anime",
                            label="模型",
                            info="isnet-anime 专为动漫角色优化；u2net 更通用",
                        )
                        bg_btn = gr.Button("开始处理", variant="primary", size="lg")
                    with gr.Column(scale=2):
                        bg_output = gr.Gallery(
                            label="处理结果",
                            columns=3,
                            height="auto",
                            object_fit="contain",
                        )
                bg_btn.click(remove_bg, inputs=[bg_input, bg_model], outputs=bg_output)

            # ==================== Boundary Crop ====================
            with gr.Tab("边界裁剪"):
                gr.Markdown(
                    "自动检测角色边界并裁剪掉多余空白。建议先用「背景去除」处理后再使用本功能，效果更佳。"
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        bc_input = gr.File(
                            label="上传图片",
                            file_types=["image"],
                            file_count="multiple",
                        )
                        bc_btn = gr.Button("开始裁剪", variant="primary", size="lg")
                    with gr.Column(scale=2):
                        bc_output = gr.Gallery(
                            label="裁剪结果",
                            columns=3,
                            height="auto",
                            object_fit="contain",
                        )
                bc_btn.click(boundary_crop, inputs=[bc_input], outputs=bc_output)

            # ==================== Smart Crop ====================
            with gr.Tab("智能裁剪"):
                gr.Markdown(
                    "基于人脸检测的智能裁剪。自动识别角色面部并按比例裁剪，支持多人图自动分割为多张。"
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        sc_input = gr.File(
                            label="上传图片",
                            file_types=["image"],
                            file_count="multiple",
                        )
                        sc_method = gr.Radio(
                            choices=["auto (YOLO)", "auto-fast (Cascade)"],
                            value="auto (YOLO)",
                            label="检测方法",
                            info="YOLO 精度更高；Cascade 速度更快",
                        )
                        sc_scale = gr.Slider(
                            0.5,
                            3.0,
                            value=1.5,
                            step=0.1,
                            label="裁剪比例",
                            info="数值越大，保留面部周围区域越广",
                        )
                        sc_btn = gr.Button("开始裁剪", variant="primary", size="lg")
                    with gr.Column(scale=2):
                        sc_output = gr.Gallery(
                            label="裁剪结果",
                            columns=3,
                            height="auto",
                            object_fit="contain",
                        )
                sc_btn.click(
                    smart_crop,
                    inputs=[sc_input, sc_method, sc_scale],
                    outputs=sc_output,
                )

            # ==================== Image Tagging ====================
            with gr.Tab("图片标注"):
                gr.Markdown(
                    "使用 WD Tagger 自动生成 Booru 风格标签，可直接用于 Stable Diffusion 训练。"
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        tag_input = gr.Image(label="上传图片", type="numpy")
                        tag_conf = gr.Slider(
                            0.1,
                            1.0,
                            value=0.5,
                            step=0.05,
                            label="置信度阈值",
                            info="越高越精确，但可能遗漏部分标签",
                        )
                        tag_btn = gr.Button("生成标签", variant="primary", size="lg")
                    with gr.Column(scale=1):
                        tag_output = gr.Textbox(
                            label="标签（逗号分隔，可直接复制使用）",
                            lines=8,
                        )
                        tag_ratings = gr.Textbox(label="分类评级", lines=4)
                tag_btn.click(
                    tag_image,
                    inputs=[tag_input, tag_conf],
                    outputs=[tag_output, tag_ratings],
                )

            # ==================== Rename ====================
            with gr.Tab("批量重命名"):
                gr.Markdown(
                    "将上传的图片按顺序编号重命名（如 `illust_0.jpg`, `illust_1.jpg`, …）。"
                )
                with gr.Row():
                    with gr.Column(scale=1):
                        rn_input = gr.File(
                            label="上传图片",
                            file_types=["image"],
                            file_count="multiple",
                        )
                        rn_prefix = gr.Textbox(
                            value="illust",
                            label="命名前缀",
                            placeholder="illust",
                        )
                        rn_btn = gr.Button("重命名", variant="primary", size="lg")
                    with gr.Column(scale=1):
                        rn_output = gr.File(
                            label="下载重命名后的图片", file_count="multiple"
                        )
                rn_btn.click(
                    rename_images,
                    inputs=[rn_input, rn_prefix],
                    outputs=rn_output,
                )

    return app


if __name__ == "__main__":
    demo = build_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
        theme=gr.themes.Soft(),
    )
