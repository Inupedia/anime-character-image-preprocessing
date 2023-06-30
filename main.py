import sys
from module import *

ACTIONS = {
    "--pixiv-user": lambda id_or_keyword: ImageCrawler("User", id_or_keyword).run(),
    "--pixiv-keyword": lambda id_or_keyword: ImageCrawler(
        "Keyword", id_or_keyword
    ).run(),
    "--rename": lambda _: ImageRenamer().run(),
    "--boundary-crop": lambda _: ImageCropper("boundary-crop")
    .create_cropper()
    .crop_and_save_all(),
    "--remove-bg": lambda _: ImageProcessor(
        model_name=IMAGE_CONFIG["REMBG_MODEL"]
    ).process_images(),
    "--smart-crop": {
        "face-only": lambda _: ImageCropper("smart-crop")
        .create_cropper()
        .crop_and_save_all(process_func=SmartCropper().face_image_process),
        "auto": lambda _: ImageCropper("smart-crop")
        .create_cropper()
        .crop_and_save_all(process_func=SmartCropper().smart_image_process),
        "auto-fast": lambda _: ImageCropper("smart-crop")
        .create_cropper()
        .crop_and_save_all(process_func=SmartCropper().smart_image_process_fast),
    },
    "--tag": lambda _: ImageTagger().process_directory(),
}

if __name__ == "__main__":
    args = sys.argv[1:]  # ignore the script name itself

    while args:
        arg = args.pop(0)
        if arg in ACTIONS:
            if arg in ["--pixiv-user", "--pixiv-keyword"]:
                keyword_or_id = args.pop(0) if args else None
            elif arg == "--smart-crop":
                method = args.pop(0) if args else None
                keyword_or_id = None
            else:
                keyword_or_id = None
            if arg == "--smart-crop" and method:
                ACTIONS[arg][method](keyword_or_id)
            else:
                ACTIONS[arg](keyword_or_id)
        else:
            print(f"Unknown argument: {arg}")
