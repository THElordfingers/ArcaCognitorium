#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/git_widget.py                                          ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/git_widget.py
# Branch, status, last commit, diff, log, commit, push, pull, fetch.
# Live streaming output via Popen + QTimer polling.
# Pre-commit file picker. Lock file detection and clearing.
# version: 1.2.0

import subprocess
import threading
from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QTextEdit, QLineEdit, QSizePolicy, QScrollArea,
    QWidget, QCheckBox, QPushButton,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QTextCursor

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG, C_PANEL,
    C_STATUS_OK, C_STATUS_ERROR, C_STATUS_WARN, C_TEAL, C_CRIMSON,
    arcane_button, micro_label,
)

POLL_INTERVAL_MS = 15_000
STREAM_POLL_MS   = 80     # output panel refresh rate during live ops


# ---------------------------------------------------------------------------
# Worker — runs a git command in a thread, streams output via signals
# ---------------------------------------------------------------------------

class _GitWorker(QObject):
    line_out   = pyqtSignal(str)   # stdout/stderr line
    finished   = pyqtSignal(int)   # returncode

    def __init__(self, cmd: list[str], cwd: str):
        super().__init__()
        self._cmd = cmd
        self._cwd = cwd

    def run(self) -> None:
        try:
            proc = subprocess.Popen(
                self._cmd,
                cwd=self._cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in proc.stdout:
                self.line_out.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode)
        except Exception as e:
            self.line_out.emit(f"✕  {e}")
            self.finished.emit(1)


class _GitThread(QThread):
    line_out  = pyqtSignal(str)
    finished  = pyqtSignal(int)

    def __init__(self, cmd: list[str], cwd: str):
        super().__init__()
        self._cmd = cmd
        self._cwd = cwd

    def run(self) -> None:
        try:
            proc = subprocess.Popen(
                self._cmd,
                cwd=self._cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            for line in proc.stdout:
                self.line_out.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode)
        except Exception as e:
            self.line_out.emit(f"✕  {e}")
            self.finished.emit(1)


# ---------------------------------------------------------------------------
# GitWidget
# ---------------------------------------------------------------------------

class GitWidget(ArcaneWidget):
    git_status_updated = pyqtSignal(str, str)

    def __init__(self, widget_id: str, repo_path: Path, parent=None,
                 poll_interval_ms: int = POLL_INTERVAL_MS):
        super().__init__(widget_id, "Git", parent)
        self._repo_path    = Path(repo_path)
        self._diff_visible = False
        self._op_running   = False
        self._active_thread: _GitThread | None = None
        self._build_body()
        self._setup_timer(poll_interval_ms)
        self.refresh()

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Branch + status
        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self._branch_label = QLabel("⎇  —")
        self._branch_label.setStyleSheet(
            f"color: {C_GOLD}; font-family: Georgia, serif; font-size: 11px;"
        )
        row1.addWidget(self._branch_label)
        row1.addStretch()
        self._status_badge = QLabel("—")
        self._status_badge.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 10px;"
        )
        row1.addWidget(self._status_badge)
        L.addLayout(row1)

        L.addWidget(self._sep())

        # Last commit
        L.addWidget(micro_label("last commit"))
        self._commit_msg = QLabel("—")
        self._commit_msg.setWordWrap(True)
        self._commit_msg.setStyleSheet(
            f"color: {C_TEXT}; font-family: Georgia, serif; font-size: 10px;"
        )
        L.addWidget(self._commit_msg)
        self._commit_age = QLabel("")
        self._commit_age.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 9px;"
        )
        L.addWidget(self._commit_age)

        L.addWidget(self._sep())

        # Commit message input
        L.addWidget(micro_label("commit message"))
        self._commit_input = QLineEdit()
        self._commit_input.setPlaceholderText("message…")
        self._commit_input.setStyleSheet(
            f"QLineEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK}; font-family: Georgia, serif;"
            f"  font-size: 10px; padding: 3px 6px; }}"
            f"QLineEdit:focus {{ border-color: {C_GOLD}; }}"
        )
        self._commit_input.returnPressed.connect(self._do_commit)
        L.addWidget(self._commit_input)

        # Action buttons row A
        row_a = QHBoxLayout()
        row_a.setSpacing(4)
        self._btn_commit = arcane_button("✦ COMMIT", accent=C_TEAL)
        self._btn_push   = arcane_button("⬆ PUSH",   accent=C_GOLD)
        self._btn_pull   = arcane_button("⬇ PULL",   accent=C_GOLD)
        self._btn_fetch  = arcane_button("⚙ FETCH",  accent=C_GOLD_DIM)
        for btn in (self._btn_commit, self._btn_push, self._btn_pull, self._btn_fetch):
            btn.setFixedHeight(24)
            row_a.addWidget(btn)
        row_a.addStretch()
        L.addLayout(row_a)

        # Action buttons row B
        row_b = QHBoxLayout()
        row_b.setSpacing(4)
        self._btn_status  = arcane_button("☰ STATUS")
        self._btn_diff    = arcane_button("⎇ DIFF")
        self._btn_log     = arcane_button("⎇ LOG")
        self._btn_refresh = arcane_button("↺")
        for btn in (self._btn_status, self._btn_diff, self._btn_log, self._btn_refresh):
            btn.setFixedHeight(24)
            row_b.addWidget(btn)
        row_b.addStretch()
        L.addLayout(row_b)

        # File picker (hidden by default)
        self._picker_frame = QFrame()
        self._picker_frame.setStyleSheet(
            f"QFrame {{ background: {C_BG}; border: 1px solid {C_GOLD_DARK}; }}"
        )
        self._picker_frame.setVisible(False)
        picker_layout = QVBoxLayout(self._picker_frame)
        picker_layout.setContentsMargins(4, 4, 4, 4)
        picker_layout.setSpacing(2)

        picker_header = QHBoxLayout()
        picker_lbl = micro_label("select files to stage")
        picker_header.addWidget(picker_lbl)
        picker_header.addStretch()
        self._btn_stage_selected = arcane_button("✦ STAGE SELECTED", accent=C_TEAL)
        self._btn_stage_selected.setFixedHeight(22)
        self._btn_stage_selected.clicked.connect(self._stage_selected)
        picker_header.addWidget(self._btn_stage_selected)
        btn_picker_close = arcane_button("✕")
        btn_picker_close.setFixedHeight(22)
        btn_picker_close.clicked.connect(lambda: self._picker_frame.setVisible(False))
        picker_header.addWidget(btn_picker_close)
        picker_layout.addLayout(picker_header)

        self._picker_scroll = QScrollArea()
        self._picker_scroll.setWidgetResizable(True)
        self._picker_scroll.setFixedHeight(160)
        self._picker_scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )
        self._picker_inner = QWidget()
        self._picker_inner.setStyleSheet(f"background: {C_BG};")
        self._picker_inner_layout = QVBoxLayout(self._picker_inner)
        self._picker_inner_layout.setContentsMargins(2, 2, 2, 2)
        self._picker_inner_layout.setSpacing(1)
        self._picker_scroll.setWidget(self._picker_inner)
        picker_layout.addWidget(self._picker_scroll)
        L.addWidget(self._picker_frame)

        # Output area
        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setVisible(False)
        self._output.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._output.setStyleSheet(
            f"QTextEdit {{ background: {C_BG}; color: {C_TEXT};"
            f"  border: 1px solid {C_GOLD_DARK};"
            f"  font-family: 'Courier New', monospace; font-size: 10px; padding: 4px; }}"
        )
        self._output.setFont(QFont("Courier New", 10))
        L.addWidget(self._output)

        # Wire
        self._btn_commit.clicked.connect(self._do_commit)
        self._btn_push.clicked.connect(self._do_push)
        self._btn_pull.clicked.connect(self._do_pull)
        self._btn_fetch.clicked.connect(self._do_fetch)
        self._btn_status.clicked.connect(self._show_file_picker)
        self._btn_diff.clicked.connect(self._toggle_diff)
        self._btn_log.clicked.connect(self._show_log)
        self._btn_refresh.clicked.connect(self.refresh)

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------

    def _setup_timer(self, ms: int) -> None:
        self._timer = QTimer(self)
        self._timer.setInterval(ms)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()

    # ------------------------------------------------------------------
    # Lock detection
    # ------------------------------------------------------------------

    def _lock_path(self) -> Path:
        return self._repo_path / ".git" / "index.lock"

    def _check_lock(self) -> bool:
        """Returns True if lock exists. Offers to clear it via output panel."""
        if not self._lock_path().exists():
            return False
        self._show_output(
            "⚠  index.lock exists — another git process may be running.\n"
            "   If no git process is active, this is a stale lock from a crashed operation.\n\n"
            "   Clearing lock and retrying…"
        )
        try:
            self._lock_path().unlink()
        except Exception as e:
            self._show_output(f"✕  Could not remove lock: {e}")
            return True
        return False   # cleared — safe to proceed

    # ------------------------------------------------------------------
    # Git helpers — quick reads (blocking, short timeout)
    # ------------------------------------------------------------------

    def _git(self, *args: str) -> str:
        try:
            r = subprocess.run(
                ["git", "-C", str(self._repo_path), *args],
                capture_output=True, text=True, timeout=15,
            )
            return r.stdout.strip()
        except Exception:
            return ""

    def _git_run(self, *args: str) -> tuple[str, str, int]:
        try:
            r = subprocess.run(
                ["git", "-C", str(self._repo_path), *args],
                capture_output=True, text=True, timeout=30,
            )
            return r.stdout.strip(), r.stderr.strip(), r.returncode
        except Exception as e:
            return "", str(e), 1

    # ------------------------------------------------------------------
    # Streaming git op via QThread
    # ------------------------------------------------------------------

    def _run_streaming(
        self,
        args: list[str],
        label: str,
        on_success=None,
        on_failure=None,
    ) -> None:
        """Run a git command in a QThread, streaming output live."""
        if self._op_running:
            self._show_output("⚠  Operation already in progress.")
            return

        self._op_running = True
        self._show_output(f"▶  git {' '.join(args)}\n")
        self.set_status("warn", f"{label}…")
        self._set_op_buttons(False)

        thread = _GitThread(
            ["git", "-C", str(self._repo_path)] + args,
            str(self._repo_path),
        )
        self._active_thread = thread

        def on_line(line: str) -> None:
            cursor = self._output.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(line + "\n")
            self._output.setTextCursor(cursor)
            self._output.ensureCursorVisible()

        def on_done(rc: int) -> None:
            self._op_running = False
            self._set_op_buttons(True)
            self._active_thread = None
            if rc == 0:
                self.set_status("ok", f"{label} complete")
                cursor = self._output.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(f"\n✦  {label} complete.")
                self._output.setTextCursor(cursor)
                if on_success:
                    on_success()
            else:
                self.set_status("error", f"{label} failed")
                cursor = self._output.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                cursor.insertText(f"\n✕  {label} failed (exit {rc}).")
                self._output.setTextCursor(cursor)
                if on_failure:
                    on_failure()

        thread.line_out.connect(on_line)
        thread.finished.connect(on_done)
        thread.start()

    def _set_op_buttons(self, enabled: bool) -> None:
        for btn in (self._btn_commit, self._btn_push, self._btn_pull, self._btn_fetch):
            btn.setEnabled(enabled)

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def _show_output(self, text: str) -> None:
        self._output.setPlainText(text)
        self._output.setVisible(True)
        self._diff_visible = True

    def _append_output(self, text: str) -> None:
        cursor = self._output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(text)
        self._output.setTextCursor(cursor)
        self._output.ensureCursorVisible()

    def _hide_output(self) -> None:
        self._output.setVisible(False)
        self._diff_visible = False

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def refresh(self) -> None:
        if self._op_running:
            return

        self.set_status("warn", "Refreshing…")

        if not (self._repo_path / ".git").exists():
            self._branch_label.setText("⎇  not a repo")
            self._status_badge.setText("—")
            self._commit_msg.setText(str(self._repo_path))
            self._commit_age.setText("")
            self.set_status("error", "Not a git repo")
            return

        branch = self._git("rev-parse", "--abbrev-ref", "HEAD") or "—"
        self._branch_label.setText(f"⎇  {branch}")

        porcelain = self._git("status", "--porcelain")
        if porcelain:
            count = len([l for l in porcelain.splitlines() if l.strip()])
            self._status_badge.setText(f"● {count} changed")
            self.set_status("warn", f"{count} uncommitted change(s)")
            self.git_status_updated.emit(self.widget_id, "warn")
        else:
            self._status_badge.setText("✦ Clean")
            self.set_status("ok", "Working tree clean")
            self.git_status_updated.emit(self.widget_id, "ok")

        log_line = self._git("log", "-1", "--pretty=format:%s|||%ar")
        if log_line:
            parts = log_line.split("|||", 1)
            msg = parts[0][:72] + ("…" if len(parts[0]) > 72 else "")
            self._commit_msg.setText(msg)
            self._commit_age.setText(parts[1] if len(parts) > 1 else "")
        else:
            self._commit_msg.setText("—")
            self._commit_age.setText("")

        if self._diff_visible:
            self._load_diff()

    # ------------------------------------------------------------------
    # File picker
    # ------------------------------------------------------------------

    def _show_file_picker(self) -> None:
        """Populate and show the pre-commit file picker."""
        porcelain = self._git("status", "--porcelain")
        if not porcelain:
            self._show_output("✦  Working tree is clean — nothing to stage.")
            return

        # Clear existing checkboxes
        while self._picker_inner_layout.count():
            item = self._picker_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._file_checks: list[tuple[QCheckBox, str, str]] = []

        for line in porcelain.splitlines():
            if not line.strip():
                continue
            xy   = line[:2]
            path = line[3:].strip()
            # Status prefix colour
            if xy.startswith("?"):
                colour = C_GOLD_DIM   # untracked
                prefix = "?"
            elif xy.startswith("D") or xy.endswith("D"):
                colour = C_CRIMSON    # deleted
                prefix = "D"
            else:
                colour = C_TEAL       # modified/added
                prefix = "M"

            cb = QCheckBox(f"  {path}")
            cb.setChecked(True)
            cb.setStyleSheet(
                f"QCheckBox {{ color: {colour}; font-family: 'Courier New', monospace; "
                f"font-size: 9px; background: {C_BG}; }}"
                f"QCheckBox::indicator {{ width: 12px; height: 12px; }}"
                f"QCheckBox::indicator:unchecked {{ border: 1px solid {C_GOLD_DARK}; background: {C_BG}; }}"
                f"QCheckBox::indicator:checked {{ border: 1px solid {C_TEAL}; background: {C_TEAL}; }}"
            )
            self._picker_inner_layout.addWidget(cb)
            self._file_checks.append((cb, path, prefix))

        self._picker_inner_layout.addStretch()
        self._picker_frame.setVisible(True)

    def _stage_selected(self) -> None:
        """Stage only the checked files."""
        if not hasattr(self, "_file_checks"):
            return

        selected = [path for cb, path, _ in self._file_checks if cb.isChecked()]
        if not selected:
            self._show_output("✕  No files selected.")
            return

        self._picker_frame.setVisible(False)

        # Stage selected files individually
        self._show_output(f"▶  Staging {len(selected)} file(s)…\n")
        errors = []
        for path in selected:
            _, err, rc = self._git_run("add", "--", path)
            if rc != 0:
                errors.append(f"  ✕ {path}: {err}")
            else:
                self._append_output(f"  ✦ staged: {path}\n")

        if errors:
            self._append_output("\n" + "\n".join(errors))
            self.set_status("warn", "Some files failed to stage")
        else:
            self._append_output(f"\n✦  {len(selected)} file(s) staged.")
            self.set_status("ok", "Staged")
        self.refresh()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _do_commit(self) -> None:
        msg = self._commit_input.text().strip()
        if not msg:
            self._show_output("✕  Commit message is empty.")
            return

        # Lock check
        if self._check_lock():
            return

        self._picker_frame.setVisible(False)

        # Check if anything is staged; if not, stage all
        staged = self._git("diff", "--cached", "--name-only")
        if not staged:
            # Nothing explicitly staged — use git add -A
            self._show_output("▶  Nothing staged — running git add -A…\n")
            _, err, rc = self._git_run("add", "-A")
            if rc != 0:
                self._show_output(f"✕  git add failed:\n{err}")
                self.set_status("error", "Stage failed")
                return
            self._append_output("✦  Staged all changes.\n\n")

        def on_success():
            self._commit_input.clear()
            self.refresh()

        self._run_streaming(
            ["commit", "-m", msg],
            label="Commit",
            on_success=on_success,
        )

    def _do_push(self) -> None:
        if self._check_lock():
            return
        self._run_streaming(["push"], label="Push", on_success=self.refresh)

    def _do_pull(self) -> None:
        if self._check_lock():
            return
        self._run_streaming(["pull"], label="Pull", on_success=self.refresh)

    def _do_fetch(self) -> None:
        if self._check_lock():
            return
        self._run_streaming(["fetch", "--prune"], label="Fetch", on_success=self.refresh)

    def _toggle_diff(self) -> None:
        if self._diff_visible:
            self._hide_output()
            self._btn_diff.setText("⎇ DIFF")
        else:
            self._load_diff()
            self._btn_diff.setText("⎇ DIFF ▲")

    def _load_diff(self) -> None:
        raw = self._git("diff", "--stat", "HEAD") or self._git("diff", "--stat")
        self._show_output(raw or "— working tree clean —")

    def _show_log(self) -> None:
        log = self._git("log", "--oneline", "--graph", "--decorate", "-25")
        self._show_output(log or "— no log —")
        self._btn_diff.setText("⎇ DIFF ▲")

    def set_repo_path(self, path: Path) -> None:
        self._repo_path = Path(path)
        self.refresh()
