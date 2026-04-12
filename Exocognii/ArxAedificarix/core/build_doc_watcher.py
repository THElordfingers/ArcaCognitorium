"""
Build Doc Watcher — watches Dolium export directory for new build documents.

When Dolium exports a completed idea as a Documentum Aedificii, this watcher
detects the new file and emits a Qt signal so Arx can offer it as context.
version: 1.0.0
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import NamedTuple

from PyQt6.QtCore import QObject, QFileSystemWatcher, pyqtSignal

log = logging.getLogger("arx.build_doc_watcher")


class BuildDoc(NamedTuple):
    path: Path
    title: str
    summary: str


class BuildDocWatcher(QObject):
    """
    Watches the Dolium exports directory for .json build docs.
    Emits doc_available when a new document is detected.
    """
    doc_available = pyqtSignal(object)       # BuildDoc
    docs_changed  = pyqtSignal(list)         # list[BuildDoc]

    def __init__(self, exports_dir: Path, parent: QObject | None = None):
        super().__init__(parent)
        self._dir = exports_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._known: set[str] = set()

        self._watcher = QFileSystemWatcher(self)
        self._watcher.addPath(str(self._dir))
        self._watcher.directoryChanged.connect(self._on_dir_changed)

        # Initial scan
        self._scan()

    def list_available(self) -> list[BuildDoc]:
        """Return all valid build docs in the exports directory."""
        docs: list[BuildDoc] = []
        for p in sorted(self._dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            doc = self._parse(p)
            if doc:
                docs.append(doc)
        return docs

    def _scan(self) -> None:
        """Scan directory and update known set."""
        current = {p.name for p in self._dir.glob("*.json")}
        new_files = current - self._known
        self._known = current
        for name in new_files:
            doc = self._parse(self._dir / name)
            if doc:
                self.doc_available.emit(doc)
        self.docs_changed.emit(self.list_available())

    def _on_dir_changed(self, _path: str) -> None:
        self._scan()

    @staticmethod
    def _parse(path: Path) -> BuildDoc | None:
        """Parse a Dolium export JSON into a BuildDoc."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            title = data.get("title") or data.get("display_name") or path.stem
            summary = data.get("summary") or data.get("declaration") or ""
            return BuildDoc(path=path, title=str(title), summary=str(summary)[:200])
        except (json.JSONDecodeError, OSError):
            return None
