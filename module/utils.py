"""Shared utilities used across modules."""

import logging
import os
from typing import List

from PIL import Image

logger = logging.getLogger(__name__)


def list_image_files(directory: str) -> List[str]:
    """List all valid image files in a directory, sorted by name."""
    image_files = []
    for filename in sorted(os.listdir(directory)):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        try:
            with Image.open(filepath) as img:
                img.verify()
            image_files.append(filename)
        except (IOError, SyntaxError):
            pass
    return image_files
