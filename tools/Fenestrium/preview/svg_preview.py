"""
preview/svg_preview.py

Exports the rendered widget tree to an SVG file using the subprocess
renderer, then opens it with xdg-open (Linux) for external viewing.
Also returns the SVG path for display in the UI.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Optional

from subprocess_preview import render_svg

SVG_OUTPUT_DIR = Path.home() / ".config" / "fenestrium" / "exports"


def export_svg(full_code: str, filename: str = "preview.svg") -> tuple[bool, str]:
    """
    Render the widget tree to an SVG file.

    Returns:
        (success: bool, message: str)
        On success, message is the path to the exported file.
        On failure, message is the error description.
    """
    SVG_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SVG_OUTPUT_DIR / filename

    success, content = render_svg(full_code)
    if not success:
        return False, content

    if not content.strip().startswith("<svg"):
        return False, "Output does not appear to be valid SVG."

    out_path.write_text(content, encoding="utf-8")

    # Open with system viewer (non-blocking)
    try:
        os.system(f"xdg-open {out_path} &")
    except Exception:
        pass  # Viewer open is best-effort

    return True, str(out_path)
