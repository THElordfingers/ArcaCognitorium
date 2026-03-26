"""
preview/subprocess_preview.py

Renders the current widget tree by:
  1. Writing a minimal Textual app to a temp file
  2. Running it headlessly with COLUMNS/LINES set
  3. Capturing the SVG screenshot via App.export_screenshot()
  4. Returning the SVG string (or ANSI fallback)

Isolated — a crash in the previewed widget cannot affect Fenestrium.
Latency: ~300–800ms. Triggered on demand, not on every keystroke.
"""
from __future__ import annotations
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Optional


# Terminal dimensions for the preview render
PREVIEW_COLS = 72
PREVIEW_ROWS = 30


def _build_preview_script(widget_code: str) -> str:
    """
    Wrap the generated compose() code in a minimal runnable Textual app
    that exports an SVG screenshot and exits immediately.
    """
    return textwrap.dedent(f"""\
        import sys, os
        os.environ.setdefault("COLUMNS", "{PREVIEW_COLS}")
        os.environ.setdefault("LINES",   "{PREVIEW_ROWS}")

        from textual.app import App, ComposeResult

        {textwrap.indent(widget_code, "        ")}

        class _PreviewApp(App):
            def compose(self) -> ComposeResult:
                # Re-use the user's compose body directly
                yield _root_widget()

            async def on_mount(self) -> None:
                svg = self.export_screenshot()
                print(svg, end="")
                self.exit()

        if __name__ == "__main__":
            _PreviewApp().run()
    """)


def _build_standalone_script(full_code: str) -> str:
    """
    For the subprocess preview we wrap the full generated code so that
    the widget is instantiated and immediately screenshot'd.
    """
    return textwrap.dedent(f"""\
        import os
        os.environ.setdefault("COLUMNS", "{PREVIEW_COLS}")
        os.environ.setdefault("LINES",   "{PREVIEW_ROWS}")

        from textual.app import App, ComposeResult

        {full_code}

        # ── Preview harness ────────────────────────────────────────
        import asyncio

        class _PreviewWrapper(App):
            def compose(self) -> ComposeResult:
                try:
                    inst = MyLayout()
                    yield inst
                except Exception as e:
                    from textual.widgets import Label
                    yield Label(f"[red]Preview error:[/] {{e}}")

            async def on_mount(self) -> None:
                svg = self.export_screenshot()
                import sys
                print(svg, end="", file=sys.stdout)
                self.exit()

        if __name__ == "__main__":
            _PreviewWrapper().run()
    """)


def render_svg(full_code: str, timeout: float = 5.0) -> tuple[bool, str]:
    """
    Run the generated code in a subprocess and capture the SVG output.

    Returns:
        (success: bool, content: str)
        On success, content is the SVG string.
        On failure, content is the error message.
    """
    script = _build_standalone_script(full_code)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="fenestrium_preview_",
        delete=False, encoding="utf-8",
    ) as f:
        f.write(script)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "COLUMNS": str(PREVIEW_COLS), "LINES": str(PREVIEW_ROWS)},
        )
        if result.returncode == 0 and result.stdout.strip():
            return True, result.stdout
        else:
            err = result.stderr.strip() or "No output produced."
            return False, f"Preview failed (exit {result.returncode}):\n{err}"
    except subprocess.TimeoutExpired:
        return False, f"Preview timed out after {timeout}s."
    except Exception as e:
        return False, f"Preview error: {e}"
    finally:
        Path(tmp_path).unlink(missing_ok=True)
