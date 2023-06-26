import sys
from module import *

ACTIONS = {
    "--pixiv": lambda id: ImageCrawler(id).run(),
    "--rename": lambda _: ImageRenamer().run(),
    "--crop": lambda _: ImageCropper(
        image_directory=IMAGE_CONFIG["CROP_INPUT_DIR"],
        save_directory=IMAGE_CONFIG["CROP_OUTPUT_DIR"],
    ).crop_and_save_all(),
    "--remove-bg": lambda _: ImageProcessor(
        model_name=IMAGE_CONFIG["REMBG_MODEL"]
    ).process_images(),
}

if __name__ == "__main__":
    args = sys.argv[1:]  # ignore the script name itself

    while args:
        arg = args.pop(0)
        if arg in ACTIONS:
            if arg == "--pixiv":
                artist_id = args.pop(0) if args else input("Please input artist id: ")
            else:
                artist_id = None
            ACTIONS[arg](artist_id)
        else:
            print(f"Unknown argument: {arg}")
