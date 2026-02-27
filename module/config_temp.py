"""Configuration template — copy to config.py and customize."""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ImageConfig:
    REMBG_MODEL: str = "u2net"
    IMAGE_PREFIX: str = "illust"
    BOUNDARY_CROP_INPUT_DIR: str = "./src/rm_bg_output/"
    BOUNDARY_CROP_OUTPUT_DIR: str = "./src/boundary_crop_output/"
    SMART_CROP_INPUT_DIR: str = "./src/rm_bg_output/"
    SMART_CROP_OUTPUT_DIR: str = "./src/smart_crop_output/"
    KEYWORD_ORDER: bool = True          # True: popular / False: latest
    KEYWORD_N_PAGES: int = 5            # 1 page = 60 images
    KEYWORD_MODE: str = "safe"          # safe / r18 / all
    IMAGE_TAGGER_INPUT_DIR: str = "./src/input/"
    IMAGE_TAGGER_CONFIDENCE: float = 0.5
    UPSCALE_INPUT_DIR: str = "./src/input/"
    UPSCALE_OUTPUT_DIR: str = "./src/upscale_output/"
    UPSCALE_SCALE: float = 4.0
    HF_REPO_ID: str = "inupedia/anime-character-image-preprocessing"
    HF_MODEL_DIR: str = "./module/model/"


@dataclass
class OutputConfig:
    VERBOSE: bool = False
    PRINT_ERROR: bool = False


@dataclass
class NetworkConfig:
    PROXY: Dict[str, str] = field(default_factory=lambda: {"https": "127.0.0.1:7890"})
    HEADER: Dict[str, str] = field(default_factory=lambda: {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/101.0.4951.54 Safari/537.36"
        ),
    })


@dataclass
class UserConfig:
    USER_ID: str = "YOUR_USER_ID"
    COOKIE: str = "YOUR_COOKIE"


@dataclass
class DownloadConfig:
    STORE_PATH: str = "./src/input/"
    N_TIMES: int = 10
    FAIL_DELAY: float = 1
    N_THREAD: int = 12
    THREAD_DELAY: float = 1


IMAGE_CONFIG = ImageConfig()
OUTPUT_CONFIG = OutputConfig()
NETWORK_CONFIG = NetworkConfig()
USER_CONFIG = UserConfig()
DOWNLOAD_CONFIG = DownloadConfig()
