"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████   █████        ██████  ██████   ██████  ███    ███ ██████  ████████     ██████  ███████ ███    ██        ██    ██ ██████   ▍
🮈  ██   ██ ██   ██       ██   ██ ██   ██ ██    ██ ████  ████ ██   ██    ██       ██       ██      ████   ██        ██    ██      ██  ▍
🮈  ██   ██ ███████ █████ ██████  ██████  ██    ██ ██ ████ ██ ██████     ██ █████ ██   ███ █████   ██ ██  ██        ██    ██  █████   ▍
🮈  ██   ██ ██   ██       ██      ██   ██ ██    ██ ██  ██  ██ ██         ██       ██    ██ ██      ██  ██ ██         ██  ██  ██       ▍
🮈  ██████  ██   ██       ██      ██   ██  ██████  ██      ██ ██         ██        ██████  ███████ ██   ████ ███████  ████   ███████  ▍
🮈                                                                                                                                    ▍
🮈                                                                                                                                    ▍
🮈                                                           Python Script                                                            ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# Devoted Absurd — Full ClaudeBox System (Local Integration)
# Uses local ClaudeBox directory + full evolution, memory, tools, chaining
"""
import sys
import os
import uuid

# 🔴 IMPORTANT: point to your local ClaudeBox
CLAUDEBOX_PATH = "/home/lordfingers/ArcaCognitorium/claudebox/"
sys.path.append(CLAUDEBOX_PATH)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel, QListWidget, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

# local import
from client import ClaudeBox


class MainWindow(QMainWindow):
    token_signal = pyqtSignal(str)
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Devoted Absurd — Full System")
        self.setMinimumSize(1200, 800)

        self.box = ClaudeBox()
        self.sessions = {}
        self.session_memory = {}  # stores weaknesses / tendencies
        self.current_session = None
        self.auto_queue = []
        self.running_chain = False

        self.box.on_token(self._on_token)
        self.box.on_response(self._on_done)
        self.box.on_error(self._on_error)

        self.token_signal.connect(self._append_token)
        self.done_signal.connect(self._on_complete)
        self.error_signal.connect(self._show_error)

        self._build_ui()

    # ── UI ─────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        main = QHBoxLayout(root)

        left = QVBoxLayout()
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.switch_session)

        self.new_btn = QPushButton("NEW ENTRY")
        self.new_btn.clicked.connect(self.new_session)

        left.addWidget(self.session_list)
        left.addWidget(self.new_btn)

        right = QVBoxLayout()

        self.role = QLineEdit()
        self.role.setPlaceholderText("Role")

        self.personality = QLineEdit()
        self.personality.setPlaceholderText("Personality")

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes / direction")

        self.generate_btn = QPushButton("GENERATE")
        self.generate_btn.clicked.connect(self.generate)

        self.auto_btn = QPushButton("AUTO EVOLVE (SMART)")
        self.auto_btn.clicked.connect(self.auto_evolve)

        self.feedback = QLineEdit()
        self.feedback.setPlaceholderText("Manual feedback")

        self.apply_btn = QPushButton("APPLY")
        self.apply_btn.clicked.connect(self.apply_feedback)

        art_row = QHBoxLayout()
        directions = {
            "Brutalist": "Make forms harsher, heavier, more brutalist",
            "Minimal": "Reduce noise, simplify shapes",
            "Darker": "Push palette darker, avoid brightness",
            "Contrast": "Increase contrast with restrained accents"
        }

        for k, v in directions.items():
            btn = QPushButton(k)
            btn.clicked.connect(lambda _, txt=v: self.apply_direction(txt))
            art_row.addWidget(btn)

        self.output = QTextEdit()
        self.status = QLabel("Ready")

        right.addWidget(self.role)
        right.addWidget(self.personality)
        right.addWidget(self.notes)
        right.addWidget(self.generate_btn)
        right.addWidget(self.auto_btn)
        right.addLayout(art_row)
        right.addWidget(self.feedback)
        right.addWidget(self.apply_btn)
        right.addWidget(self.output)
        right.addWidget(self.status)

        main.addLayout(left, 1)
        main.addLayout(right, 3)

        self.setCentralWidget(root)

    # ── SESSION ─────────────────────────────────────────

    def new_session(self):
        sid = f"session_{uuid.uuid4().hex[:6]}"
        name = f"Entry {len(self.sessions)+1}"
        self.sessions[sid] = name
        self.session_memory[sid] = []
        self.session_list.addItem(name)
        self.current_session = sid
        self.output.clear()

    def switch_session(self, item):
        for sid, name in self.sessions.items():
            if name == item.text():
                self.current_session = sid
                break
        self.output.clear()

    # ── GENERATION ─────────────────────────────────────────

    def generate(self):
        if not self.current_session:
            self.new_session()

        self.output.clear()
        self.status.setText("Generating...")

        memory_bias = "\n".join(self.session_memory[self.current_session])

        prompt = f"""
Generate a character prompt.

Role: {self.role.text()}
Personality: {self.personality.text()}
Notes: {self.notes.toPlainText()}

Avoid these issues:\n{memory_bias}

Color rules:
- dark, earthy, desaturated
- strong midtones
- 1–2 sharp accents
- no pastel

Be specific and concrete.
"""

        self.box.send_threaded(prompt, session_id=self.current_session)

    # ── AUTO EVOLUTION (CHAINED) ─────────────────────────

    def auto_evolve(self):
        if not self.current_session:
            return

        self.status.setText("Auto evolving...")

        self.auto_queue = [
            "Refine the previous prompt. Increase specificity.",
            "Critique the prompt. List weaknesses briefly.",
            "Rewrite the prompt fixing those weaknesses.",
            "Push colour contrast slightly but keep palette restrained."
        ]

        self.running_chain = True
        self._run_next()

    def _run_next(self):
        if not self.auto_queue:
            self.running_chain = False
            return

        step = self.auto_queue.pop(0)
        self.box.send_threaded(step, session_id=self.current_session)

    # ── FEEDBACK ─────────────────────────────────────────

    def apply_feedback(self):
        txt = self.feedback.text().strip()
        if not txt:
            return

        self.box.send_threaded(
            f"Apply this direction and rewrite fully: {txt}",
            session_id=self.current_session
        )

    def apply_direction(self, txt):
        self.box.send_threaded(txt, session_id=self.current_session)

    # ── EVENTS ─────────────────────────────────────────

    def _on_token(self, token):
        self.token_signal.emit(token.text)

    def _on_done(self, response):
        # capture weaknesses if present
        text = str(response)
        if "weakness" in text.lower():
            self.session_memory[self.current_session].append(text[:200])

        self.done_signal.emit()

        if self.running_chain:
            self._run_next()

    def _on_error(self, err):
        self.error_signal.emit(str(err))

    # ── UI ─────────────────────────────────────────

    def _append_token(self, t):
        self.output.insertPlainText(t)

    def _on_complete(self):
        self.status.setText("Done")

    def _show_error(self, e):
        self.status.setText(f"Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
