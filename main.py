"""Entry point for the image preprocessing tool.

Supports both the new subcommand style (``python main.py rename``) and the
legacy ``--flag`` style (``python main.py --rename``) for backward compatibility.
"""

import sys

from module.cli import main


def _translate_legacy_args(argv: list[str]) -> list[str]:
    """Convert legacy ``--flag`` style arguments to subcommand style.

    Examples:
        ["--rename"]                   → ["rename"]
        ["--remove-bg"]                → ["remove-bg"]
        ["--smart-crop", "auto", "1.5"] → ["smart-crop", "auto", "1.5"]
        ["--pixiv-user", "12345"]      → ["pixiv-user", "12345"]
        ["--rename", "--remove-bg"]    → not translated (multi-command)
    """
    flag_map = {
        "--rename": "rename",
        "--remove-bg": "remove-bg",
        "--boundary-crop": "boundary-crop",
        "--smart-crop": "smart-crop",
        "--tag": "tag",
        "--pixiv-user": "pixiv-user",
        "--pixiv-keyword": "pixiv-keyword",
    }

    if not argv:
        return argv

    flags_found = [a for a in argv if a in flag_map]
    if len(flags_found) != 1:
        return argv

    result = []
    for arg in argv:
        if arg in flag_map:
            result.append(flag_map[arg])
        else:
            result.append(arg)
    return result


if __name__ == "__main__":
    argv = sys.argv[1:]

    flags_in_argv = [a for a in argv if a.startswith("--") and a in {
        "--rename", "--remove-bg", "--boundary-crop",
        "--smart-crop", "--tag", "--pixiv-user", "--pixiv-keyword",
    }]

    if len(flags_in_argv) > 1:
        from module.config import IMAGE_CONFIG
        from module.image_processor import ImageProcessor
        from module.image_renamer import ImageRenamer
        from module.image_cropper import ImageCropper, SmartCropper
        from module.image_tagger import ImageTagger

        args = argv[:]
        while args:
            arg = args.pop(0)
            if arg == "--rename":
                ImageRenamer().run()
            elif arg == "--remove-bg":
                ImageProcessor(model_name=IMAGE_CONFIG["REMBG_MODEL"]).process_images()
            elif arg == "--boundary-crop":
                ImageCropper("boundary-crop").create_cropper().crop_and_save_all()
            elif arg == "--smart-crop":
                method = args.pop(0) if args else None
                scale = float(args.pop(0)) if args and not args[0].startswith("--") else 1.0
                if method == "auto":
                    ImageCropper("smart-crop").create_cropper().crop_and_save_all(
                        process_func=SmartCropper(scale=scale).smart_image_process
                    )
                elif method == "auto-fast":
                    ImageCropper("smart-crop").create_cropper().crop_and_save_all(
                        process_func=SmartCropper().smart_image_process_fast
                    )
            elif arg == "--tag":
                ImageTagger().process_directory()
            else:
                print(f"Unknown argument: {arg}")
    else:
        translated = _translate_legacy_args(argv)
        sys.exit(main(translated))
