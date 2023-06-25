import os
from PIL import Image
from ..config import IMAGE_CONFIG


class ImageRenamer:
    def __init__(self, folder_path="./src/input"):
        self.folder_path = folder_path
        self.image_files = self.get_image_files()

    def get_image_files(self):
        files = os.listdir(self.folder_path)
        image_files = []

        for file in files:
            file_path = os.path.join(self.folder_path, file)
            try:
                # Try to open the file with PIL
                img = Image.open(file_path)
                img.verify()  # Verify that it is, in fact an image
                image_files.append(file)
            except (IOError, SyntaxError) as e:
                # It's not an image file, so ignore it
                pass

        image_files.sort()
        return image_files

    def rename_files(self):
        for idx, filename in enumerate(self.image_files, start=1):
            basename, ext = os.path.splitext(filename)
            image_prefix = IMAGE_CONFIG["IMAGE_PREFIX"]
            new_name = f"{image_prefix}_{idx - 1}{ext}"
            old_file_path = os.path.join(self.folder_path, filename)
            new_file_path = os.path.join(self.folder_path, new_name)
            os.rename(old_file_path, new_file_path)

    def run(self):
        self.rename_files()
