import io
import logging
import os

from PIL import Image
from rembg import remove, new_session
from tqdm import tqdm

from ..utils import list_image_files

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(
        self,
        input_dir: str = "./src/input",
        output_dir: str = "./src/rm_bg_output",
        model_name: str = "u2net",
    ):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
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
