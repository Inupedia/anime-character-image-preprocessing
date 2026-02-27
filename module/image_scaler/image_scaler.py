"""Image upscaling using Real-ESRGAN."""

import logging
import os
from typing import Optional

import cv2
import numpy as np
import torch
from tqdm import tqdm

from ..config import IMAGE_CONFIG
from ..utils import list_image_files

logger = logging.getLogger(__name__)

_MODEL_FILENAME = "realesr-animevideov3.pth"
_MODEL_URL = (
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/"
    "realesr-animevideov3.pth"
)

_UPSCALER: Optional[object] = None


def _get_upscaler(scale: int = 4):
    """Lazy-load the Real-ESRGAN model (downloads on first use)."""
    global _UPSCALER
    if _UPSCALER is not None and _UPSCALER.scale == scale:
        return _UPSCALER

    from .realesrgan import RealESRGANer, SRVGGNetCompact

    model_dir = IMAGE_CONFIG.HF_MODEL_DIR
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, _MODEL_FILENAME)
    if not os.path.exists(model_path):
        logger.info("Downloading Real-ESRGAN model (~17 MB)...")
        torch.hub.download_url_to_file(_MODEL_URL, model_path)

    model = SRVGGNetCompact(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_conv=16,
        upscale=4,
        act_type="prelu",
    )

    _UPSCALER = RealESRGANer(
        scale=4,
        model_path=model_path,
        model=model,
        tile=0,
        tile_pad=10,
        pre_pad=10,
        half=False,
    )
    return _UPSCALER


class ImageScaler:
    """Upscale images using Real-ESRGAN (4× anime model)."""

    def __init__(
        self,
        input_dir: str = "./src/input",
        output_dir: str = "./src/upscale_output",
        outscale: float = 4.0,
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.outscale = outscale
        os.makedirs(self.output_dir, exist_ok=True)

    def upscale_image(self, img: np.ndarray) -> np.ndarray:
        """Upscale a single BGR numpy image and return the result."""
        upscaler = _get_upscaler()
        output, _ = upscaler.enhance(img, outscale=self.outscale)
        return output

    def process_images(self) -> None:
        """Upscale all images in *input_dir* and save to *output_dir*."""
        image_files = list_image_files(self.input_dir)
        total = len(image_files)
        logger.info("Total files to upscale: %d (scale=%.1f×)", total, self.outscale)

        processed = 0
        skipped = 0

        for filename in tqdm(image_files, desc="Upscaling images"):
            base, ext = os.path.splitext(filename)
            out_name = f"{base}_upscaled{ext}"
            out_path = os.path.join(self.output_dir, out_name)

            if os.path.exists(out_path):
                skipped += 1
                continue

            img = cv2.imread(os.path.join(self.input_dir, filename), cv2.IMREAD_UNCHANGED)
            if img is None:
                logger.warning("Cannot read image: %s", filename)
                continue

            output = self.upscale_image(img)
            cv2.imwrite(out_path, output)
            processed += 1

        logger.info(
            "Upscaling complete. Processed: %d, Skipped: %d.",
            processed,
            skipped,
        )
