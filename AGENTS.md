# AGENTS.md

## Cursor Cloud specific instructions

### Overview
Python tool for anime character image preprocessing (background removal, cropping, tagging, renaming). Supports both CLI (`python main.py <command>`) and Gradio web UI (`python app.py`).

### Python version
Requires **Python 3.11+**. Managed by **uv**; the virtualenv lives at `/workspace/.venv`.

### Running commands
```bash
uv run python app.py          # Gradio web UI on http://0.0.0.0:7860
uv run python main.py --help  # CLI help
```

### CLI usage
See `python main.py --help` for the argparse-based interface.

**Subcommand style** (preferred):
```bash
uv run python main.py rename
uv run python main.py remove-bg
uv run python main.py boundary-crop
uv run python main.py smart-crop auto [scale]
uv run python main.py tag
uv run python main.py pixiv-user <artist_id>
uv run python main.py pixiv-keyword <keyword>
```

**Legacy flag style** (backward compatible, supports chaining):
```bash
uv run python main.py --rename --remove-bg --boundary-crop
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
uv run python app.py   # launches on http://0.0.0.0:7860
```
Six tabs: 背景去除, 边界裁剪, 智能裁剪, 图片标注, 批量重命名, Pixiv 下载. Models are lazy-loaded on first use per tab.

### Gotchas
- First run of `remove-bg` downloads ~176 MB U-2-Net ONNX model to `~/.u2net/`. `smart-crop` and `tag` also download models on first use.
- Pixiv crawler features require valid credentials in `module/config.py` and network access — skip for local testing.
- Image scaler module (Real-ESRGAN) is disabled (placeholder in `module/image_scaler/`).
- No automated test suite; validation is by running CLI commands against sample images.
- `dghs-imgutils` metadata says `numpy<2` but works fine with numpy 2.x; overridden in `pyproject.toml` via `[tool.uv] override-dependencies`.
- PyTorch is sourced from the CPU-only index via `[tool.uv.sources]` in `pyproject.toml` — no manual `--index-url` needed.
