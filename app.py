"""Entry point for the Gradio web UI.

Launch with::

    python app.py
"""

import logging

import gradio as gr

from webui.app import CSS, build_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

if __name__ == "__main__":
    demo = build_app()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CSS,
        theme=gr.themes.Soft(),
    )
