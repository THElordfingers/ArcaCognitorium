"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈                  ██     ██ ██ ██████   ██████  ███████ ████████      ██████  ███████  ██████  ██ ███████ ████████ ██████  ██    ██ ▍
🮈                  ██     ██ ██ ██   ██ ██       ██         ██         ██   ██ ██      ██       ██ ██         ██    ██   ██  ██  ██  ▍
🮈                  ██  █  ██ ██ ██   ██ ██   ███ █████      ██         ██████  █████   ██   ███ ██ ███████    ██    ██████    ████   ▍
🮈                  ██ ███ ██ ██ ██   ██ ██    ██ ██         ██         ██   ██ ██      ██    ██ ██      ██    ██    ██   ██    ██    ▍
🮈                   ███ ███  ██ ██████   ██████  ███████    ██ ███████ ██   ██ ███████  ██████  ██ ███████    ██    ██   ██    ██    ▍
🮈                                                                                                                                    ▍
🮈                                                                                                                                    ▍
🮈           Python Script           ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# ⯨                                                                         ⯩
# ⯨   𝐀𝐍𝐍𝐔𝐒 🟌 ＭＭＸＸＶＩ                      widget_registry.py   ⯩
# ⯨                                                                         ⯩
# ╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
# PRAESIDIUM · widget_registry.py
# Widget manifest and instantiation factory.
# version: 1.0.0
"""




from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Ensure the Praesidium package root is on sys.path so that
# `widgets.git_widget` etc. resolve correctly regardless of cwd.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from configuus import Configuus
from widget_base import ArcaneWidget

if TYPE_CHECKING:
    pass


# Registry of known widget class names → import paths.
# New widgets register themselves here.
WIDGET_MANIFEST: dict[str, str] = {
    "GitWidget":     "widgets.git_widget",
    "ChatWidget":    "widgets.chat_widget",
    "TokenTracker":  "widgets.token_tracker",
    "TodoBoard":     "widgets.todo_board",
    "AppLauncher":   "widgets.app_launcher",
    "StyleReference":"widgets.style_reference",
    "StatusLegend":  "widgets.status_legend",
}


class WidgetRegistry:
    """
    Widget manifest and instantiation factory.
    Resolves class names from WIDGET_MANIFEST and constructs instances
    with appropriate arguments extracted from the layout record.
    """

    def __init__(self, configuus: Configuus):
        self._cfg = configuus

    def instantiate(
        self,
        cls_name: str,
        widget_id: str,
        extra: dict,
        parent=None,
    ) -> ArcaneWidget | None:
        """
        Instantiate a widget by class name.

        extra: arbitrary dict of constructor kwargs from layout.json.
               Each widget class defines what it needs.

        Returns None and logs if class is unknown or construction fails.
        """
        module_path = WIDGET_MANIFEST.get(cls_name)
        if module_path is None:
            print(f"[WidgetRegistry] Unknown widget class: {cls_name!r}")
            return None

        try:
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, cls_name)
        except (ImportError, AttributeError) as e:
            print(f"[WidgetRegistry] Failed to import {cls_name} from {module_path}: {e}")
            return None

        try:
            return self._construct(cls, widget_id, extra, parent)
        except Exception as e:
            print(f"[WidgetRegistry] Construction of {cls_name}({widget_id!r}) failed: {e}")
            return None

    def _construct(self, cls, widget_id: str, extra: dict, parent) -> ArcaneWidget:
        """Dispatch construction by class name."""
        name = cls.__name__
        stor = self._cfg.arca_repo_path.parent / "Praesidium" / "storage"

        if name == "GitWidget":
            repo_path = Path(extra.get("repo_path") or str(self._cfg.arca_repo_path))
            return cls(widget_id=widget_id, repo_path=repo_path, parent=parent)

        if name == "ChatWidget":
            return cls(widget_id=widget_id, configuus=self._cfg, parent=parent)

        if name in ("TokenTracker", "TodoBoard"):
            return cls(widget_id=widget_id, storage_path=stor, parent=parent)

        if name == "AppLauncher":
            apps = self._cfg.get("launcher_apps") or None
            return cls(widget_id=widget_id, apps=apps, parent=parent)

        # StyleReference, StatusLegend — no extra args
        return cls(widget_id=widget_id, parent=parent)

    def available_classes(self) -> list[str]:
        return list(WIDGET_MANIFEST.keys())
