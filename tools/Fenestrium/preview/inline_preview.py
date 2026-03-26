"""
preview/inline_preview.py

Builds a widget instance from the generated code by exec()'ing it
in an isolated namespace, then returns the instantiated widget for
mounting directly inside Fenestrium's Specularium pane.

Faster than subprocess (~immediate), but runs in-process.
Exceptions are caught and surfaced as a Label widget.
"""
from __future__ import annotations
import traceback
from typing import Optional

from textual.widget import Widget
from textual.widgets import Label, Static


def build_widget(full_code: str) -> Widget:
    """
    Execute full_code in an isolated namespace and return the instantiated
    MyLayout widget. Returns an error Label on any failure.
    """
    namespace: dict = {}
    try:
        exec(full_code, namespace)
        cls = namespace.get("MyLayout")
        if cls is None:
            return Label("[yellow]No MyLayout class in generated code.[/]", markup=True)
        instance = cls()
        return instance
    except SyntaxError as e:
        return Label(
            f"[red bold]Syntax error:[/]\n{e.msg} (line {e.lineno})",
            markup=True,
        )
    except Exception:
        tb = traceback.format_exc(limit=4)
        return Label(
            f"[red bold]Runtime error:[/]\n[dim]{tb}[/]",
            markup=True,
        )
