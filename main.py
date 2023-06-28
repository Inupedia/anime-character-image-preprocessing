import sys
from module import *

ACTIONS = {
    "--pixiv-user": lambda id_or_keyword: ImageCrawler("User", id_or_keyword).run(),
    "--pixiv-keyword": lambda id_or_keyword: ImageCrawler(
        "Keyword", id_or_keyword
    ).run(),
    "--rename": lambda _: ImageRenamer().run(),
    "--crop": lambda _: ImageCropper(
        image_directory=IMAGE_CONFIG["CROP_INPUT_DIR"],
        save_directory=IMAGE_CONFIG["CROP_OUTPUT_DIR"],
    ).crop_and_save_all(),
    "--remove-bg": lambda _: ImageProcessor(
        model_name=IMAGE_CONFIG["REMBG_MODEL"]
    ).process_images(),
    "--smartcrop": lambda _: SmartCropper().process_directory(
        IMAGE_CONFIG["SMARTCROP_INPUT_DIR"]
    ),
}

if __name__ == "__main__":
    args = sys.argv[1:]  # ignore the script name itself

    while args:
        arg = args.pop(0)
        if arg in ACTIONS:
            if arg in ["--pixiv-user", "--pixiv-keyword"]:
                keyword_or_id = args.pop(0) if args else None
            else:
                keyword_or_id = None
            ACTIONS[arg](keyword_or_id)
        else:
            print(f"Unknown argument: {arg}")
