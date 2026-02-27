"""Individual Gradio tab components.

Each sub-module exposes a ``create_tab()`` function that builds
its UI inside a ``gr.Tab`` context and wires up event handlers.
"""

from . import boundary_crop, remove_bg, rename, smart_crop, tagging

__all__ = ["remove_bg", "boundary_crop", "smart_crop", "tagging", "rename"]
