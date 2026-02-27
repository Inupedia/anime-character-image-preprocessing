"""Command-line interface for the image preprocessing tool."""

import argparse
import logging
import sys
from typing import List, Optional

from .config import IMAGE_CONFIG
from .image_processor import ImageProcessor
from .image_renamer import ImageRenamer
from .image_crawler import ImageCrawler
from .image_cropper import ImageCropper, SmartCropper
from .image_tagger import ImageTagger
from .image_scaler import ImageScaler


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sd-preprocess",
        description="Anime character image preprocessing tool for Stable Diffusion training datasets.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output.",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("rename", help="Rename images with a sequential prefix.")

    subparsers.add_parser("remove-bg", help="Remove image backgrounds using rembg.")

    subparsers.add_parser("boundary-crop", help="Crop images to character boundaries.")

    smart_crop_parser = subparsers.add_parser("smart-crop", help="Smart crop images around detected faces.")
    smart_crop_parser.add_argument(
        "method",
        choices=["auto", "auto-fast"],
        help="'auto' uses YOLO face detection; 'auto-fast' uses OpenCV cascade classifier.",
    )
    smart_crop_parser.add_argument(
        "scale",
        type=float,
        nargs="?",
        default=1.0,
        help="Scale factor for crop area (default: 1.0).",
    )

    subparsers.add_parser("tag", help="Generate tags for images using ONNX tagger model.")

    upscale_parser = subparsers.add_parser("upscale", help="Upscale images using Real-ESRGAN.")
    upscale_parser.add_argument(
        "scale",
        type=float,
        nargs="?",
        default=4.0,
        help="Output scale factor (default: 4.0).",
    )

    pixiv_user_parser = subparsers.add_parser("pixiv-user", help="Download all artworks from a Pixiv artist.")
    pixiv_user_parser.add_argument("artist_id", help="Pixiv artist ID.")

    pixiv_keyword_parser = subparsers.add_parser("pixiv-keyword", help="Download artworks by keyword search.")
    pixiv_keyword_parser.add_argument("keyword", help="Search keyword.")

    return parser


def run_command(command: str, **kwargs) -> None:
    """Execute a single command by name."""
    logger = logging.getLogger(__name__)

    match command:
        case "rename":
            ImageRenamer().run()

        case "remove-bg":
            ImageProcessor(model_name=IMAGE_CONFIG.REMBG_MODEL).process_images()

        case "boundary-crop":
            ImageCropper.create("boundary-crop").crop_and_save_all()

        case "smart-crop":
            method = kwargs.get("method", "auto")
            scale = kwargs.get("scale", 1.0)
            cropper = ImageCropper.create("smart-crop")
            if method == "auto":
                cropper.crop_and_save_all(
                    process_func=SmartCropper(scale=scale).smart_image_process
                )
            elif method == "auto-fast":
                cropper.crop_and_save_all(
                    process_func=SmartCropper().smart_image_process_fast
                )

        case "tag":
            ImageTagger().process_directory()

        case "upscale":
            scale = kwargs.get("scale", IMAGE_CONFIG.UPSCALE_SCALE)
            ImageScaler(
                input_dir=IMAGE_CONFIG.UPSCALE_INPUT_DIR,
                output_dir=IMAGE_CONFIG.UPSCALE_OUTPUT_DIR,
                outscale=scale,
            ).process_images()

        case "pixiv-user":
            ImageCrawler("User", kwargs["artist_id"]).run()

        case "pixiv-keyword":
            ImageCrawler("Keyword", kwargs["keyword"]).run()

        case _:
            logger.error("Unknown command: %s", command)


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        run_command(args.command, **{k: v for k, v in vars(args).items() if k != "command" and k != "verbose"})
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
        return 130
    except Exception:
        logger.exception("An error occurred")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
