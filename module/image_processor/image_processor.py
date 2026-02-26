import io
import logging
import os
from typing import List

from PIL import Image
from rembg import remove, new_session
from tqdm import tqdm

logger = logging.getLogger(__name__)


def list_image_files(directory: str) -> List[str]:
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


class ImageProcessor:
    def __init__(
        self,
        input_dir: str = "./src/input",
        output_dir: str = "./src/rm_bg_output",
        model_name: str = "u2net",
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model_name = model_name
        self.session = new_session(self.model_name)

    def process_images(self) -> None:
        image_files = list_image_files(self.input_dir)

        total_files = len(image_files)
        logger.info("Total files to process: %d", total_files)

        processed_files = 0
        skipped_files = 0

        for filename in tqdm(image_files, desc="Processing images"):
            base_name, _ = os.path.splitext(filename)
            output_filename = f"{base_name}_character.png"
            output_path = os.path.join(self.output_dir, output_filename)

            if os.path.exists(output_path):
                skipped_files += 1
                continue

            input_path = os.path.join(self.input_dir, filename)
            with open(input_path, "rb") as f:
                input_data = f.read()

            img = Image.open(io.BytesIO(input_data))
            byte_arr = io.BytesIO()
            img.save(byte_arr, format="PNG")
            png_data = byte_arr.getvalue()

            output_data = remove(
                png_data,
                session=self.session,
                post_process_mask=True,
                bgcolor=(255, 255, 255, 255),
            )

            with open(output_path, "wb") as f:
                f.write(output_data)

            processed_files += 1

        logger.info(
            "Processing complete. Processed files: %d. Skipped files: %d.",
            processed_files,
            skipped_files,
        )
