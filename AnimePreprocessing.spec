# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for packaging the Gradio app as a standalone executable.

Usage::

    pip install pyinstaller
    pyinstaller AnimePreprocessing.spec
"""

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

# ---------------------------------------------------------------------------
# Data files that must be bundled
# ---------------------------------------------------------------------------
datas = [
    ("module/image_cropper/lbpcascade_animeface.xml", "module/image_cropper"),
    ("module/config_temp.py", "module"),
]

if os.path.exists("module/config.py"):
    datas.append(("module/config.py", "module"))

# ---------------------------------------------------------------------------
# Hidden imports — modules loaded lazily inside functions
# ---------------------------------------------------------------------------
hiddenimports = (
    collect_submodules("module")
    + collect_submodules("webui")
    + [
        "rembg",
        "onnxruntime",
        "scipy",
        "scipy.special",
        "skimage",
        "pymatting",
    ]
)

# ---------------------------------------------------------------------------
# Packages that ship data / native binaries (Gradio frontend, etc.)
# ---------------------------------------------------------------------------
binaries = []

for pkg in ("gradio", "gradio_client", "safehttpx", "groovy"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AnimePreprocessing",
    debug=False,
    strip=False,
    upx=True,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="AnimePreprocessing",
)
