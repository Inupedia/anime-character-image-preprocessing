import cv2
import os
from PIL import Image
from tqdm import tqdm
import numpy as np
from ..config import IMAGE_CONFIG


class BoundaryCropper:
    def __init__(self):
        self.image_directory = IMAGE_CONFIG["BOUNDARY_CROP_INPUT_DIR"]
        self.save_directory = IMAGE_CONFIG["BOUNDARY_CROP_OUTPUT_DIR"]
        self.image_files = []
        self.load_all_images()

    def get_character_bounding_box(self, image) -> tuple:
        # convert image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # apply Otsu's thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # find contours in the thresholded image
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Create bounding box for all contours
        boxes = [cv2.boundingRect(c) for c in contours]
        x = min([b[0] for b in boxes])
        y = min([b[1] for b in boxes])
        w = max([b[0] + b[2] for b in boxes]) - x
        h = max([b[1] + b[3] for b in boxes]) - y

        return x, y, w, h

    def load_all_images(self):
        all_files = os.listdir(self.image_directory)
        for filename in all_files:
            try:
                Image.open(
                    os.path.join(self.image_directory, filename)
                )  # Try to open the file with PIL
                self.image_files.append(
                    filename
                )  # If it succeeds, add the filename to the list
            except IOError:
                pass  # If it fails, ignore the file

    def crop_and_save_all(self):
        for filename in tqdm(self.image_files, desc="Processing images"):
            image_path = os.path.join(self.image_directory, filename)
            img = Image.open(image_path)
            image_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            x, y, w, h = self.get_character_bounding_box(image_cv)
            cropped_img = img.crop((x, y, x + w, y + h))
            base_name, ext = os.path.splitext(os.path.basename(image_path))
            save_path = os.path.join(
                self.save_directory, f"{base_name}_boundary_crop{ext}"
            )
            cropped_img.save(save_path)
