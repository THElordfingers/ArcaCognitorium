"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈  ██████   █████        ██████  ██████   ██████  ███    ███ ██████  ████████    ██    ██ ██████   ▍
🮈  ██   ██ ██   ██       ██   ██ ██   ██ ██    ██ ████  ████ ██   ██    ██       ██    ██      ██  ▍
🮈  ██   ██ ███████ █████ ██████  ██████  ██    ██ ██ ████ ██ ██████     ██ █████ ██    ██  █████   ▍
🮈  ██   ██ ██   ██       ██      ██   ██ ██    ██ ██  ██  ██ ██         ██        ██  ██  ██       ▍
🮈  ██████  ██   ██       ██      ██   ██  ██████  ██      ██ ██         ██         ████   ███████  ▍
🮈                                                                                                  ▍
🮈                                                                                                  ▍
🮈                                          Python Script                                           ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
████████████████████████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░█
🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃
# ClaudeBox Evolution App (Advanced — Multi-Session + Auto Evolution + Art Director)
"""
import sys
import uuid
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel, QListWidget, QHBoxLayout
)
from PyQt6.QtCore import pyqtSignal

from claudebox import ClaudeBox


class MainWindow(QMainWindow):
    token_signal = pyqtSignal(str)
    done_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Devoted Absurd — Evolution System")
        self.setMinimumSize(1100, 750)

        self.box = ClaudeBox()
        self.sessions = {}  # id -> name
        self.current_session = None

        # ClaudeBox events
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

        # LEFT: session list
        left = QVBoxLayout()
        self.session_list = QListWidget()
        self.session_list.itemClicked.connect(self.switch_session)

        self.new_session_btn = QPushButton("NEW ENTRY")
        self.new_session_btn.clicked.connect(self.new_session)

        left.addWidget(self.session_list)
        left.addWidget(self.new_session_btn)

        # RIGHT: controls
        right = QVBoxLayout()

        self.role = QLineEdit()
        self.role.setPlaceholderText("Role")

        self.personality = QLineEdit()
        self.personality.setPlaceholderText("Personality")

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("Notes / direction")

        self.generate_btn = QPushButton("GENERATE")
        self.generate_btn.clicked.connect(self.generate)

        self.auto_btn = QPushButton("AUTO EVOLVE")
        self.auto_btn.clicked.connect(self.auto_evolve)

        self.refine_btn = QPushButton("REFINE")
        self.refine_btn.clicked.connect(self.refine)

        self.feedback = QLineEdit()
        self.feedback.setPlaceholderText("Manual feedback")

        self.apply_feedback_btn = QPushButton("APPLY FEEDBACK")
        self.apply_feedback_btn.clicked.connect(self.apply_feedback)

        # Art director buttons
        art_row = QHBoxLayout()
        for label in ["More Brutalist", "Reduce Noise", "Darker Palette", "Increase Contrast"]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, l=label: self.apply_art_direction(l))
            art_row.addWidget(btn)

        self.output = QTextEdit()
        self.status = QLabel("Ready")

        right.addWidget(self.role)
        right.addWidget(self.personality)
        right.addWidget(self.notes)
        right.addWidget(self.generate_btn)
        right.addWidget(self.auto_btn)
        right.addWidget(self.refine_btn)
        right.addLayout(art_row)
        right.addWidget(self.feedback)
        right.addWidget(self.apply_feedback_btn)
        right.addWidget(self.output)
        right.addWidget(self.status)

        main.addLayout(left, 1)
        main.addLayout(right, 3)

        self.setCentralWidget(root)

    # ── SESSION MANAGEMENT ─────────────────────────

    def new_session(self):
        sid = f"session_{uuid.uuid4().hex[:6]}"
        name = f"Entry {len(self.sessions)+1}"
        self.sessions[sid] = name
        self.session_list.addItem(name)
        self.current_session = sid
        self.output.clear()

    def switch_session(self, item):
        name = item.text()
        for sid, n in self.sessions.items():
            if n == name:
                self.current_session = sid
                break
        self.output.clear()

    # ── CORE ACTIONS ─────────────────────────

    def generate(self):
        if not self.current_session:
            self.new_session()

        self.output.clear()
        self.status.setText("Generating...")

        prompt = f"""
Generate a character prompt.

Role: {self.role.text()}
Personality: {self.personality.text()}
Notes: {self.notes.toPlainText()}

Color direction:
- dark, earthy, desaturated base
- strong midtones
- 1–2 controlled accent colours
- no pastel tones

Style:
- stylized 2D
- bold ink outlines
- flat cel shading
- grounded proportions

Be specific. Avoid generic phrasing.
"""

        self.box.send_threaded(prompt, session_id=self.current_session)

    def refine(self):
        self.status.setText("Refining...")

        self.box.send_threaded(
            "Refine the previous prompt. Increase specificity and improve contrast using restrained accents.",
            session_id=self.current_session
        )

    def apply_feedback(self):
        text = self.feedback.text().strip()
        if not text:
            return

        self.status.setText("Applying feedback...")

        self.box.send_threaded(
            f"Apply this direction and rewrite the prompt fully: {text}",
            session_id=self.current_session
        )

    def apply_art_direction(self, label):
        mapping = {
            "More Brutalist": "Make forms heavier, harsher, more brutalist",
            "Reduce Noise": "Simplify design, remove unnecessary detail",
            "Darker Palette": "Shift palette darker, reduce brightness",
            "Increase Contrast": "Increase contrast using restrained accent colours"
        }

        self.box.send_threaded(mapping[label], session_id=self.current_session)

    # ── AUTO EVOLUTION ─────────────────────────

    def auto_evolve(self):
        self.status.setText("Auto evolving...")

        steps = [
            "Refine the previous prompt. Increase clarity and specificity.",
            "Critique the prompt briefly, then rewrite it improved.",
            "Push colour contrast slightly while keeping palette restrained."
        ]

        for step in steps:
            self.box.send_threaded(step, session_id=self.current_session)

    # ── EVENTS ─────────────────────────

    def _on_token(self, token):
        self.token_signal.emit(token.text)

    def _on_done(self, response):
        self.done_signal.emit()

    def _on_error(self, err):
        self.error_signal.emit(str(err))

    # ── UI UPDATES ─────────────────────────

    def _append_token(self, text):
        self.output.insertPlainText(text)

    def _on_complete(self):
        self.status.setText("Done")

    def _show_error(self, err):
        self.status.setText(f"Error: {err}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


