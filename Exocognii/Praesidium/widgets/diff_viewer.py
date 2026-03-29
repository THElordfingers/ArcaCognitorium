#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/diff_viewer.py                                         ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/diff_viewer.py
# Git diff renderer + arbitrary file diff via drop.
# Colour-coded unified diff. Syntax highlights code blocks via inline CSS.
# version: 1.0.0

import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QTextEdit, QHBoxLayout, QVBoxLayout, QFrame,
    QComboBox, QLineEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)


class DiffViewer(ArcaneWidget):
    """
    Unified diff renderer.
    Source modes:
      - git: diff against HEAD, staged, or between refs
      - file: drop two files to diff them
    """

    def __init__(self, widget_id: str, repo_path: Path | None = None, parent=None):
        super().__init__(widget_id, "Diff Viewer", parent)
        self._repo_path  = Path(repo_path) if repo_path else None
        self._drop_paths: list[str] = []
        self._build_body()
        self.setAcceptDrops(True)
        self.set_status("idle", "")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Source selector row
        row1 = QHBoxLayout()
        row1.setSpacing(6)
        row1.addWidget(micro_label("source"))

        self._src_combo = QComboBox()
        self._src_combo.addItems(["GIT UNSTAGED", "GIT STAGED", "GIT HEAD~1", "GIT REFS", "FILES"])
        self._src_combo.setStyleSheet(
            f"QComboBox {{ background: {C_BG}; color: {C_GOLD};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 2px 6px; }}"
            f"QComboBox QAbstractItemView {{"
            f"  background: {C_PANEL}; color: {C_TEXT};"
            f"  selection-background-color: {C_GOLD_DARK}; }}"
        )
        self._src_combo.currentTextChanged.connect(self._on_source_changed)
        row1.addWidget(self._src_combo)

        btn_refresh = arcane_button("↺")
        btn_refresh.setFixedHeight(22)
        btn_refresh.clicked.connect(self.refresh)
        row1.addWidget(btn_refresh)
        row1.addStretch()
        L.addLayout(row1)

        # Ref input (shown only for GIT REFS mode)
        self._ref_row = QHBoxLayout()
        self._ref_row.setSpacing(6)
        self._ref_row.addWidget(micro_label("refs"))
        self._ref_a = QLineEdit()
        self._ref_a.setPlaceholderText("HEAD~1")
        self._ref_b = QLineEdit()
        self._ref_b.setPlaceholderText("HEAD")
        for inp in (self._ref_a, self._ref_b):
            inp.setStyleSheet(
                f"QLineEdit {{ background: {C_BG}; color: {C_TEXT};"
                f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
                f"  font-size: 10px; padding: 2px 6px; }}"
                f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
            )
            inp.returnPressed.connect(self.refresh)
            self._ref_row.addWidget(inp)
        L.addLayout(self._ref_row)
        self._set_ref_row_visible(False)

        # File drop hint (FILES mode)
        self._file_hint = QFrame()
        self._file_hint.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 1px dashed {C_GOLD_DARK}; }}"
        )
        from PyQt6.QtWidgets import QLabel
        hint_layout = QVBoxLayout(self._file_hint)
        lbl = QLabel("Drop two files to diff")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 10px;"
            "font-style: italic; border: none;"
        )
        hint_layout.addWidget(lbl)
        self._drop_label = lbl
        L.addWidget(self._file_hint)
        self._file_hint.setVisible(False)

        L.addWidget(self._sep())

        # Diff output
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._output.setFont(QFont("Courier New", 10))
        self._output.setStyleSheet(
            f"QTextEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: none; font-family: 'Courier New', monospace;"
            f"  font-size: 10px; padding: 4px; }}"
        )
        L.addWidget(self._output, 1)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    def _set_ref_row_visible(self, visible: bool) -> None:
        for i in range(self._ref_row.count()):
            item = self._ref_row.itemAt(i)
            if item and item.widget():
                item.widget().setVisible(visible)

    # ------------------------------------------------------------------
    # Source change
    # ------------------------------------------------------------------

    def _on_source_changed(self, text: str) -> None:
        is_refs  = (text == "GIT REFS")
        is_files = (text == "FILES")
        self._set_ref_row_visible(is_refs)
        self._file_hint.setVisible(is_files)
        if not is_files:
            self.refresh()

    # ------------------------------------------------------------------
    # Git helpers
    # ------------------------------------------------------------------

    def _git(self, *args: str) -> tuple[str, int]:
        if not self._repo_path:
            return "✕  No repo path configured.", 1
        try:
            r = subprocess.run(
                ["git", "-C", str(self._repo_path), *args],
                capture_output=True, text=True, timeout=15,
            )
            out = r.stdout or r.stderr
            return out.strip(), r.returncode
        except Exception as e:
            return str(e), 1

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        mode = self._src_combo.currentText()

        if mode == "GIT UNSTAGED":
            raw, rc = self._git("diff")
        elif mode == "GIT STAGED":
            raw, rc = self._git("diff", "--cached")
        elif mode == "GIT HEAD~1":
            raw, rc = self._git("diff", "HEAD~1", "HEAD")
        elif mode == "GIT REFS":
            a = self._ref_a.text().strip() or "HEAD~1"
            b = self._ref_b.text().strip() or "HEAD"
            raw, rc = self._git("diff", a, b)
        else:
            return   # FILES mode — driven by drops

        if not raw:
            raw = "— no diff —"
        self._render(raw)
        self.set_status("ok" if rc == 0 else "warn", "")

    # ------------------------------------------------------------------
    # Renderer
    # ------------------------------------------------------------------

    def _render(self, content: str) -> None:
        html_lines = []
        for line in content.splitlines():
            if line.startswith('+') and not line.startswith('+++'):
                colour = "#2a6a2a"
            elif line.startswith('-') and not line.startswith('---'):
                colour = "#6a2a2a"
            elif line.startswith('@@'):
                colour = "#1a5a5a"
            elif line.startswith('diff ') or line.startswith('index ') or line.startswith('---') or line.startswith('+++'):
                colour = "#7a6a2a"
            else:
                colour = C_GOLD_DIM
            esc = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            html_lines.append(
                f'<div style="color:{colour};white-space:pre;font-family:Courier New,monospace;font-size:10px">{esc}</div>'
            )
        self._output.setHtml("".join(html_lines))

    # ------------------------------------------------------------------
    # File drop diff
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        for url in urls:
            p = url.toLocalFile()
            if p and p not in self._drop_paths:
                self._drop_paths.append(p)

        if len(self._drop_paths) >= 2:
            self._diff_files(self._drop_paths[0], self._drop_paths[1])
            self._drop_paths = []
        else:
            self._drop_label.setText(
                f"✦  {Path(self._drop_paths[0]).name} — drop second file"
            )

    def _diff_files(self, a: str, b: str) -> None:
        try:
            r = subprocess.run(
                ["diff", "-u", a, b],
                capture_output=True, text=True,
            )
            raw = r.stdout or "— files are identical —"
            self._render(raw)
            self._drop_label.setText("Drop two files to diff")
            self.set_status("ok", f"{Path(a).name} ↔ {Path(b).name}")
        except Exception as e:
            self.set_status("error", str(e)[:60])

    def set_repo_path(self, path: Path) -> None:
        self._repo_path = Path(path)
        self.refresh()
