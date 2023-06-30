import sys
from module import *

ACTIONS = {
    "--pixiv-user": lambda id_or_keyword: ImageCrawler("User", id_or_keyword).run(),
    "--pixiv-keyword": lambda id_or_keyword: ImageCrawler("Keyword", id_or_keyword).run(),
    "--rename": lambda _: ImageRenamer().run(),
    "--boundary-crop": lambda _: ImageCropper("boundary-crop").create_cropper().crop_and_save_all(),
    "--remove-bg": lambda _: ImageProcessor(model_name=IMAGE_CONFIG["REMBG_MODEL"]).process_images(),
    "--smart-crop": lambda args: smart_crop_handler(args),
    "--tag": lambda _: ImageTagger().process_directory(),
}

def smart_crop_handler(args):
    method = args.pop(0) if args else None
    scale = float(args.pop(0)) if args else 1.0

    if method == "auto":
        ImageCropper("smart-crop").create_cropper().crop_and_save_all(
            process_func=SmartCropper(scale=scale).smart_image_process
        )
    elif method == "auto-fast":
        ImageCropper("smart-crop").create_cropper().crop_and_save_all(
            process_func=SmartCropper().smart_image_process_fast
        )
    else:
        print(f"Unknown smart-crop method: {method}")

if __name__ == "__main__":
    args = sys.argv[1:]  # ignore the script name itself

    while args:
        arg = args.pop(0)
        if arg in ACTIONS:
            if arg == "--smart-crop":
                smart_crop_handler(args)
            else:
                ACTIONS[arg](args)
        else:
            print(f"Unknown argument: {arg}")
