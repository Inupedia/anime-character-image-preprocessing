# AGENTS.md

## Cursor Cloud specific instructions

### Overview
This is a Python CLI tool for anime character image preprocessing (background removal, cropping, tagging, renaming). It is **not** a web app or service — it is invoked via `python main.py` with various flags.

### Python version
The project requires **Python 3.11** (pinned `torch==2.0.1` is incompatible with Python 3.12+). A virtualenv at `/workspace/venv` is created with Python 3.11 from the `deadsnakes` PPA.

### Activating the environment
```bash
source /workspace/venv/bin/activate
```

### Configuration
`module/config.py` must exist (copied from `module/config_temp.py`). The update script handles this automatically.

### Running the tool
See the README for all flags. Common examples:
```bash
python main.py --rename
python main.py --remove-bg
python main.py --boundary-crop
python main.py --smart-crop auto
python main.py --tag
python main.py --rename --remove-bg --boundary-crop   # mixed/chained
```

### I/O directories
- Input images go in `src/input/`
- Background removal output: `src/rm_bg_output/`
- Boundary crop output: `src/boundary_crop_output/`
- Smart crop output: `src/smart_crop_output/`

### Gotchas
- The first run of `--remove-bg` downloads a ~176 MB ONNX model to `~/.u2net/`. Similarly, `--smart-crop` and `--tag` download models on first use.
- The Pixiv crawler (`--pixiv-user`, `--pixiv-keyword`) requires valid Pixiv credentials in `module/config.py` and network/proxy access — skip these for local testing.
- The image scaler module (Real-ESRGAN) is disabled (commented out in `module/__init__.py`).
- No automated test suite exists in this repo; validation is done by running CLI commands against sample images.
- Sample images are available in `assets/` and can be copied to `src/input/` for testing.
