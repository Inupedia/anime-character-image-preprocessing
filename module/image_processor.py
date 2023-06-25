import os
import io
from PIL import Image
from rembg import remove, new_session
from .image_cropper import ImageCropper

class ImageProcessor:
    def __init__(self, input_dir='./src/input', output_dir='./src/output'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.model_name = "isnet-anime"
        self.session = new_session(self.model_name)
        self.cropper = ImageCropper()

    def process_images(self):
        # Get a list of all files in the input directory
        all_files = os.listdir(self.input_dir)

        # Filter out any files that are not valid images
        image_files = []
        for filename in all_files:
            try:
                Image.open(os.path.join(self.input_dir, filename))  # Try to open the file with PIL
                image_files.append(filename)  # If it succeeds, add the filename to the list
            except IOError:
                pass  # If it fails, ignore the file

        total_files = len(image_files)
        print(f"Total files to process: {total_files}")

        processed_files = 0
        skipped_files = 0

        # Loop over each file in the input directory
        for i, filename in enumerate(image_files, start=1):
            # Modify the filename for the output file
            base_name, extension = os.path.splitext(filename)
            output_filename = f"{base_name}_character.png"  # Always use .png extension

            # Create the full output path
            output_path = os.path.join(self.output_dir, output_filename)

            # Check if the output file already exists, if so, skip this file
            if os.path.exists(output_path):
                skipped_files += 1
                continue

            # Create the full input path and read the file
            input_path = os.path.join(self.input_dir, filename)
            with open(input_path, 'rb') as i:
                input_data = i.read()

            # Convert the image to PNG
            img = Image.open(io.BytesIO(input_data))
            byte_arr = io.BytesIO()
            img.save(byte_arr, format='PNG')
            png_data = byte_arr.getvalue()

            # Remove the background
            output_data = remove(png_data, session=self.session, post_process_mask=True, bgcolor=(255, 255, 255, 255))

            # Write the file
            with open(output_path, 'wb') as o:
                o.write(output_data)

            # Crop the image
            self.cropper.crop_and_save(output_path)

            processed_files += 1

        print(f"Processing complete. Processed files: {processed_files}. Skipped files: {skipped_files}.")
