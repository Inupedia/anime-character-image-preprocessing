"""Entry point for the image preprocessing tool.

Supports both the new subcommand style (``python main.py rename``) and the
legacy ``--flag`` style (``python main.py --rename``) for backward compatibility.
"""

import sys

from module.cli import main, run_command, setup_logging

_FLAG_MAP = {
    "--rename": "rename",
    "--remove-bg": "remove-bg",
    "--boundary-crop": "boundary-crop",
    "--smart-crop": "smart-crop",
    "--tag": "tag",
    "--pixiv-user": "pixiv-user",
    "--pixiv-keyword": "pixiv-keyword",
}


def _translate_legacy_args(argv: list[str]) -> list[str]:
    """Convert single legacy ``--flag`` to subcommand style."""
    if not argv:
        return argv
    flags_found = [a for a in argv if a in _FLAG_MAP]
    if len(flags_found) != 1:
        return argv
    return [_FLAG_MAP.get(a, a) for a in argv]


def _run_chained_legacy(argv: list[str]) -> None:
    """Execute multiple legacy ``--flag`` commands in sequence."""
    setup_logging()
    args = argv[:]
    while args:
        flag = args.pop(0)
        cmd = _FLAG_MAP.get(flag)
        if cmd is None:
            print(f"Unknown argument: {flag}")
            continue

        kwargs = {}
        if cmd == "smart-crop":
            kwargs["method"] = args.pop(0) if args else "auto"
            if args and not args[0].startswith("--"):
                kwargs["scale"] = float(args.pop(0))
            else:
                kwargs["scale"] = 1.0
        elif cmd in ("pixiv-user", "pixiv-keyword"):
            value = args.pop(0) if args else None
            if not value:
                continue
            key = "artist_id" if cmd == "pixiv-user" else "keyword"
            kwargs[key] = value

        run_command(cmd, **kwargs)


if __name__ == "__main__":
    argv = sys.argv[1:]
    flags_in_argv = [a for a in argv if a in _FLAG_MAP]

    if len(flags_in_argv) > 1:
        _run_chained_legacy(argv)
    else:
        sys.exit(main(_translate_legacy_args(argv)))
