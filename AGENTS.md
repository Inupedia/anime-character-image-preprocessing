# AGENTS.md

## Cursor Cloud specific instructions

### Overview
Python tool for anime character image preprocessing (background removal, cropping, tagging, renaming). Supports both CLI (`python main.py <command>`) and Gradio web UI (`python app.py`).

### Python version
Requires **Python 3.11** (via deadsnakes PPA). A virtualenv lives at `/workspace/venv`.

### Activating the environment
```bash
source /workspace/venv/bin/activate
```

### CLI usage
The tool supports two styles. See `python main.py --help` for the new argparse-based interface.

**New subcommand style** (preferred):
```bash
python main.py rename
python main.py remove-bg
python main.py boundary-crop
python main.py smart-crop auto [scale]
python main.py tag
python main.py pixiv-user <artist_id>
python main.py pixiv-keyword <keyword>
```

**Legacy flag style** (backward compatible, supports chaining):
```bash
python main.py --rename --remove-bg --boundary-crop
```

### Configuration
`module/config.py` must exist (copied from `module/config_temp.py`). It is gitignored. The update script creates it automatically if missing.

### I/O directories
- Input: `src/input/` — sample images available in `assets/`
- Background removal: `src/rm_bg_output/`
- Boundary crop: `src/boundary_crop_output/`
- Smart crop: `src/smart_crop_output/`

### Gradio web UI
```bash
source /workspace/venv/bin/activate
python app.py          # launches on http://0.0.0.0:7860
```
Five tabs: 背景去除 (Background Removal), 边界裁剪 (Boundary Crop), 智能裁剪 (Smart Crop), 图片标注 (Image Tagging), 批量重命名 (Batch Rename). Models are lazy-loaded on first use per tab.

### Gotchas
- First run of `remove-bg` downloads ~176 MB U-2-Net ONNX model to `~/.u2net/`. `smart-crop` and `tag` also download models on first use.
- Pixiv crawler features require valid credentials in `module/config.py` and network access — skip for local testing.
- Image scaler module (Real-ESRGAN) is disabled (placeholder in `module/image_scaler/`).
- No automated test suite; validation is by running CLI commands against sample images.
- `dghs-imgutils` metadata says `numpy<2` but works fine with numpy 2.x in practice.
- PyTorch must be installed from the CPU index (`--index-url https://download.pytorch.org/whl/cpu`) before other deps; installing from default PyPI causes dependency resolution failures due to CUDA bindings.
