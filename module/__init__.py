# -*- coding: utf-8 -*-

__author__ = """Pengju Zhang"""
__email__ = "inupedia.official@gmail.com"
__version__ = "0.1.0"

from .image_processor import ImageProcessor
from .image_renamer import ImageRenamer
from .image_crawler import ImageCrawler
from .image_cropper import BaseCropper, ImageCropper, SmartCropper, BoundaryCropper
from .image_tagger import ImageTagger
from .config import IMAGE_CONFIG, OUTPUT_CONFIG, NETWORK_CONFIG, USER_CONFIG, DOWNLOAD_CONFIG

__all__ = [
    "ImageProcessor",
    "ImageRenamer",
    "ImageCrawler",
    "BaseCropper",
    "ImageCropper",
    "SmartCropper",
    "BoundaryCropper",
    "ImageTagger",
    "IMAGE_CONFIG",
    "OUTPUT_CONFIG",
    "NETWORK_CONFIG",
    "USER_CONFIG",
    "DOWNLOAD_CONFIG",
]
