import sys
from module import *

ACTIONS = {
    "--pixiv": lambda: ImageCrawler(input("Please input artist id: ")).run(),
    "--rename": lambda: ImageRenamer().run(),
    "--crop": lambda: ImageCropper(
        image_directory=IMAGE_CONFIG["CROP_INPUT_DIR"],
        save_directory=IMAGE_CONFIG["CROP_OUTPUT_DIR"],
    ).crop_and_save_all(),
    "--remove-bg": lambda: ImageProcessor(
        model_name=IMAGE_CONFIG["REMBG_MODEL"]
    ).process_images(),
}

if __name__ == "__main__":
    args = sys.argv[1:]  # ignore the script name itself

    for arg in args:
        if arg in ACTIONS:
            ACTIONS[arg]()
        else:
            print(f"Unknown argument: {arg}")
