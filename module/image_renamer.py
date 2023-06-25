import os
from PIL import Image

class ImageRenamer:
    def __init__(self, folder_path = './src/input'):
        self.folder_path = folder_path
        self.image_files = self.get_image_files()
        self.prompt_and_rename()

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
            new_name = f'illust_{idx - 1}{ext}'
            old_file_path = os.path.join(self.folder_path, filename)
            new_file_path = os.path.join(self.folder_path, new_name)
            os.rename(old_file_path, new_file_path)

    def prompt_and_rename(self):
        response = input(f'Do you want to rename all images? (yes/no): ').lower()
        if response == 'yes':
            self.rename_files()
            