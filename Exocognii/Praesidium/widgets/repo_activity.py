#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/repo_activity.py                                       ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/repo_activity.py
# Repo activity feed — recent commits, file changes, watchdog file monitor.
# version: 1.0.0

import subprocess
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer, QFileSystemWatcher, pyqtSignal
from PyQt6.QtGui import QFont

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL, C_CRIMSON, C_STATUS_OK,
    arcane_button, micro_label,
)

POLL_MS      = 30_000   # git log poll interval
MAX_ENTRIES  = 40


class RepoActivity(ArcaneWidget):
    """
    Live repo activity feed.
    Shows recent commits (git log) + file change events via QFileSystemWatcher.
    Auto-refreshes on file changes and on a 30s timer.
    """

    def __init__(self, widget_id: str, repo_path: Path, parent=None):
        super().__init__(widget_id, "Repo Activity", parent)
        self._repo_path = Path(repo_path)
        self._entries: list[dict] = []   # {ts, kind, text, colour}
        self._build_body()
        self._setup_watcher()
        self._setup_timer()
        # Defer first refresh until widget is fully constructed and shown
        from PyQt6.QtCore import QTimer as _QT
        _QT.singleShot(100, self.refresh)

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Header row
        row = QHBoxLayout()
        row.setSpacing(6)
        self._branch_lbl = micro_label("—")
        row.addWidget(self._branch_lbl)
        row.addStretch()
        btn_refresh = arcane_button("↺")
        btn_refresh.setFixedHeight(22)
        btn_refresh.clicked.connect(self.refresh)
        row.addWidget(btn_refresh)
        btn_clear = arcane_button("✕ CLEAR")
        btn_clear.setFixedHeight(22)
        btn_clear.clicked.connect(self._clear_entries)
        row.addWidget(btn_clear)
        L.addLayout(row)
        L.addWidget(self._sep())

        # Scrollable feed
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._feed_widget = QWidget()
        self._feed_widget.setStyleSheet(f"background: {C_BG};")
        self._feed_layout = QVBoxLayout(self._feed_widget)
        self._feed_layout.setContentsMargins(0, 0, 0, 0)
        self._feed_layout.setSpacing(1)
        self._feed_layout.addStretch()
        self._scroll.setWidget(self._feed_widget)
        L.addWidget(self._scroll, 1)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Watcher + timer
    # ------------------------------------------------------------------

    def _setup_watcher(self) -> None:
        self._watcher = QFileSystemWatcher()
        git_dir = self._repo_path / ".git"
        if git_dir.exists():
            # Only watch files that actually exist — addPath on missing files
            # can segfault on some Qt6 builds
            for fname in ("COMMIT_EDITMSG", "HEAD", "index"):
                p = git_dir / fname
                if p.exists():
                    self._watcher.addPath(str(p))
        self._watcher.fileChanged.connect(self._on_file_changed)

    def _setup_timer(self) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(POLL_MS)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

    def _on_file_changed(self, path: str) -> None:
        self._add_entry("event", f"repo changed: {Path(path).name}", C_GOLD_DIM)
        self.refresh()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        self.set_status("warn", "Refreshing…")

        if not (self._repo_path / ".git").exists():
            self.set_status("error", "Not a git repo")
            return

        # Branch
        try:
            r = subprocess.run(
                ["git", "-C", str(self._repo_path), "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, timeout=8,
            )
            branch = r.stdout.strip() or "—"
        except Exception:
            branch = "—"
        self._branch_lbl.setText(f"⎇  {branch}")

        # Recent commits
        try:
            r = subprocess.run(
                ["git", "-C", str(self._repo_path),
                 "log", "--oneline", "--no-walk", "--max-count=20",
                 "--format=%h|%s|%ar|%an"],
                capture_output=True, text=True, timeout=10,
            )
            lines = r.stdout.strip().splitlines()
        except Exception:
            lines = []

        # Rebuild entries from commits (keep file-watch events)
        commit_entries = []
        for line in lines:
            parts = line.split("|", 3)
            if len(parts) < 4:
                continue
            sha, msg, age, author = parts
            msg_short = msg[:60] + ("…" if len(msg) > 60 else "")
            commit_entries.append({
                "kind":   "commit",
                "text":   f"{sha}  {msg_short}",
                "sub":    f"{author} · {age}",
                "colour": C_GOLD_DIM,
            })

        # Merge: keep event entries, replace commit block
        event_entries = [e for e in self._entries if e.get("kind") == "event"]
        self._entries = commit_entries + event_entries
        self._entries = self._entries[:MAX_ENTRIES]

        self._render_feed()
        self.set_status("ok", f"{len(commit_entries)} commits")

    # ------------------------------------------------------------------
    # Feed rendering
    # ------------------------------------------------------------------

    def _render_feed(self) -> None:
        # Clear all but stretch
        while self._feed_layout.count() > 1:
            item = self._feed_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for entry in self._entries:
            row = self._make_entry_row(entry)
            self._feed_layout.insertWidget(self._feed_layout.count() - 1, row)

    def _make_entry_row(self, entry: dict) -> QWidget:
        container = QWidget()
        container.setStyleSheet(f"background: {C_BG};")
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(0)

        kind   = entry.get("kind", "commit")
        colour = C_TEAL if kind == "event" else C_GOLD_DIM
        prefix = "⚡" if kind == "event" else "●"

        main_lbl = QLabel(f"{prefix}  {entry['text']}")
        main_lbl.setStyleSheet(
            f"color: {colour}; font-family: 'Courier New', monospace; font-size: 10px;"
        )
        main_lbl.setWordWrap(True)
        vbox.addWidget(main_lbl)

        if entry.get("sub"):
            sub_lbl = QLabel(f"    {entry['sub']}")
            sub_lbl.setStyleSheet(
                f"color: {C_GOLD_DARK}; font-family: Georgia, serif; font-size: 9px;"
            )
            vbox.addWidget(sub_lbl)

        return container

    def _add_entry(self, kind: str, text: str, colour: str) -> None:
        self._entries.insert(0, {"kind": kind, "text": text, "colour": colour})
        self._entries = self._entries[:MAX_ENTRIES]
        self._render_feed()

    def _clear_entries(self) -> None:
        self._entries = []
        self._render_feed()

    def set_repo_path(self, path: Path) -> None:
        self._repo_path = Path(path)
        self.refresh()
