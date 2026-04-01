"""
Devoted Absurd — Character Prompt Generator
PyQt6 desktop application.
v1.2 — button layout fix, RANDOM button restored
"""

import sys
import uuid
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit, QScrollArea,
    QFrame, QSplitter, QTabWidget, QGroupBox, QFormLayout, QSlider,
    QSpinBox, QStatusBar, QSizePolicy, QToolButton, QProgressBar,
    QListWidget, QListWidgetItem, QDialog, QDialogButtonBox,
    QMessageBox, QCheckBox,
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QSize,
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter,
    QFontDatabase, QIcon, QKeySequence, QShortcut, QClipboard,
)

import data_pools as dp
import learning
import claude_worker


# ── PALETTE ───────────────────────────────────────────────────────────────────
C = {
    "bg":        "#1a1c18",
    "panel":     "#202220",
    "panel2":    "#252720",
    "border":    "#333530",
    "green":     "#4a7c3f",
    "green_b":   "#7ab648",
    "amber":     "#c8a84b",
    "muted":     "#7a7f6e",
    "text":      "#d4d8c8",
    "text_dim":  "#9a9f8e",
    "red":       "#a04040",
    "teal":      "#3a7070",
    "teal_b":    "#5ab8b8",
    "highlight": "#2a3028",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background: {C['bg']};
    color: {C['text']};
    font-family: "IBM Plex Mono", "Courier New", monospace;
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {C['border']};
    background: {C['panel']};
}}
QTabBar::tab {{
    background: {C['bg']};
    color: {C['muted']};
    padding: 6px 18px;
    border: 1px solid {C['border']};
    border-bottom: none;
    font-size: 11px;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {C['panel']};
    color: {C['green_b']};
    border-bottom: 2px solid {C['green']};
}}
QGroupBox {{
    border: 1px solid {C['border']};
    margin-top: 14px;
    padding-top: 8px;
    color: {C['amber']};
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}}
QLineEdit, QTextEdit, QComboBox {{
    background: {C['panel2']};
    border: 1px solid {C['border']};
    color: {C['text']};
    padding: 5px 8px;
    font-family: "IBM Plex Mono", "Courier New", monospace;
    font-size: 12px;
    selection-background-color: {C['green']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {C['green']};
}}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox::down-arrow {{
    width: 8px; height: 8px;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid {C['muted']};
    margin-right: 4px;
}}
QComboBox QAbstractItemView {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    color: {C['text']};
    selection-background-color: {C['green']};
}}
QPushButton {{
    background: transparent;
    border: 1px solid {C['border']};
    color: {C['muted']};
    padding: 6px 14px;
    font-family: "IBM Plex Mono", "Courier New", monospace;
    font-size: 11px;
    letter-spacing: 1px;
}}
QPushButton:hover {{ border-color: {C['green']}; color: {C['green_b']}; }}
QPushButton:pressed {{ background: {C['highlight']}; }}
QPushButton#btn_generate {{
    border-color: {C['green']};
    color: {C['green_b']};
    font-size: 13px;
    letter-spacing: 2px;
    padding: 10px 24px;
    font-weight: bold;
}}
QPushButton#btn_generate:hover {{ background: rgba(74,124,63,0.2); }}
QPushButton#btn_random {{
    border-color: {C['amber']};
    color: {C['amber']};
}}
QPushButton#btn_random:hover {{ background: rgba(200,168,75,0.15); }}
QPushButton#btn_copy {{
    border-color: {C['teal']};
    color: {C['teal_b']};
}}
QPushButton#btn_copy:hover {{ background: rgba(58,112,112,0.2); }}
QPushButton#btn_iterate {{
    border-color: {C['teal']};
    color: {C['teal_b']};
    font-size: 11px;
}}
QPushButton#btn_iterate:hover {{ background: rgba(58,112,112,0.2); }}
QSlider::groove:horizontal {{
    height: 3px;
    background: {C['border']};
}}
QSlider::handle:horizontal {{
    width: 14px; height: 14px;
    margin: -6px 0;
    border-radius: 7px;
    background: {C['green_b']};
}}
QSlider::sub-page:horizontal {{ background: {C['green']}; }}
QScrollBar:vertical {{
    background: {C['bg']};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {C['border']};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 8px; background: {C['bg']}; border: none; }}
QScrollBar::handle:horizontal {{ background: {C['border']}; border-radius: 4px; }}
QProgressBar {{
    border: 1px solid {C['border']};
    background: {C['panel']};
    color: {C['green_b']};
    text-align: center;
    font-size: 10px;
}}
QProgressBar::chunk {{ background: {C['green']}; }}
QListWidget {{
    background: {C['panel']};
    border: 1px solid {C['border']};
    color: {C['text']};
    font-size: 11px;
}}
QListWidget::item {{ padding: 4px 8px; border-bottom: 1px solid {C['border']}; }}
QListWidget::item:selected {{ background: {C['highlight']}; color: {C['green_b']}; }}
QStatusBar {{
    background: {C['panel']};
    color: {C['muted']};
    border-top: 1px solid {C['border']};
    font-size: 10px;
    letter-spacing: 1px;
}}
QSplitter::handle {{ background: {C['border']}; width: 1px; height: 1px; }}
QLabel#section_label {{
    color: {C['amber']};
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-bottom: 4px;
    border-bottom: 1px solid {C['border']};
}}
QLabel#score_label {{
    color: {C['green_b']};
    font-size: 22px;
    font-weight: bold;
}}
QLabel#weakness_tag {{
    color: {C['red']};
    background: rgba(160,64,64,0.12);
    border: 1px solid rgba(160,64,64,0.3);
    padding: 2px 7px;
    font-size: 10px;
}}
"""


# ── HELPERS ───────────────────────────────────────────────────────────────────
def section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_label")
    return lbl


def hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet(f"color: {C['border']};")
    return f


def make_combo(items: list, placeholder: str = "Auto") -> QComboBox:
    cb = QComboBox()
    cb.addItem(placeholder)
    for item in items:
        cb.addItem(item)
    return cb


# ── PROMPT HIGHLIGHTER ────────────────────────────────────────────────────────
class PromptHighlighter(QSyntaxHighlighter):
    def __init__(self, doc):
        super().__init__(doc)
        self._rules = []

        def rule(pattern, color, bold=False):
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            if bold:
                fmt.setFontWeight(700)
            import re
            self._rules.append((re.compile(pattern), fmt))

        rule(r"(Stylized 2D|flat cel shading|ink outlines|bold clean)[^,.\n]*", C["green_b"])
        rule(r"(Character is|Personality:|Wearing|Build:|Pose:|Expression:)", C["amber"], bold=True)
        rule(r"(Color palette:|background)", C["teal_b"])
        rule(r"\b(no animals|no glossy|not sketchy|not painterly)\b", C["red"])

    def highlightBlock(self, text):
        for pattern, fmt in self._rules:
            for m in pattern.finditer(text):
                self.setFormat(m.start(), m.end() - m.start(), fmt)


# ── MAIN WINDOW ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    claude_done = pyqtSignal(str, dict)
    claude_error = pyqtSignal(str, str)
    claude_generated = pyqtSignal(dict)
    claude_generate_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Devoted Absurd — Character Prompt Generator")
        self.setMinimumSize(1200, 760)
        self.resize(1400, 860)

        self._current_char = None
        self._current_entry_id = None
        self._current_prompt = ""
        self._claude_result = None
        self._pending_analysis = False

        self.claude_done.connect(self._on_claude_done)
        self.claude_error.connect(self._on_claude_error)
        self.claude_generated.connect(self._on_claude_generated)
        self.claude_generate_error.connect(self._on_claude_generate_error)

        self._build_ui()
        self._setup_shortcuts()
        self.status("Ready — press GENERATE or F5")

    # ── UI BUILD ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(STYLESHEET)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        sidebar = self._build_sidebar()
        main_area = self._build_main()

        splitter.addWidget(sidebar)
        splitter.addWidget(main_area)
        splitter.setSizes([380, 860])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)

        self.setCentralWidget(splitter)
        self.setStatusBar(QStatusBar())

    def _build_sidebar(self) -> QWidget:
        outer = QWidget()
        outer.setMinimumWidth(340)
        outer.setMaximumWidth(480)
        outer_lay = QVBoxLayout(outer)
        outer_lay.setContentsMargins(0, 0, 0, 0)
        outer_lay.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ border: none; background: {C['panel']}; }}")
        outer_lay.addWidget(scroll)

        w = QWidget()
        w.setStyleSheet(f"background: {C['panel']};")
        lay = QVBoxLayout(w)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        # Title
        title = QLabel("DEVOTED ABSURD")
        title.setStyleSheet(f"color: {C['green_b']}; font-size: 18px; font-weight: bold; letter-spacing: 3px;")
        subtitle = QLabel("Character Prompt Generator")
        subtitle.setStyleSheet(f"color: {C['muted']}; font-size: 10px; letter-spacing: 1px;")
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addWidget(hline())

        # ── ARCHETYPE ──
        lay.addWidget(section_label("▶ Archetype"))
        self.combo_archetype = make_combo(
            [f"{v['label']}" for v in dp.ARCHETYPES.values()],
            placeholder="Random"
        )
        self.combo_archetype.setProperty("archetype_keys",
            ["random"] + list(dp.ARCHETYPES.keys()))
        lay.addWidget(self.combo_archetype)

        # ── CUSTOM CHARACTER ──
        lay.addWidget(section_label("▶ Custom Character (optional)"))
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Name / title...")
        self.input_role = QLineEdit()
        self.input_role.setPlaceholderText("Role / occupation (overrides archetype pool)...")
        self.input_personality = QLineEdit()
        self.input_personality.setPlaceholderText("Personality traits...")
        self.input_extra = QTextEdit()
        self.input_extra.setPlaceholderText("Extra visual / story notes...")
        self.input_extra.setMaximumHeight(70)
        for w_ in [self.input_name, self.input_role, self.input_personality, self.input_extra]:
            lay.addWidget(w_)

        # ── OVERRIDES ──
        lay.addWidget(section_label("▶ Overrides"))

        flay = QFormLayout()
        flay.setSpacing(6)
        flay.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.combo_mood = make_combo(dp.MOODS)
        self.combo_body = make_combo(dp.BODY_TYPES)
        self.combo_age = make_combo(dp.AGES)
        self.combo_gender = make_combo(["man", "woman", "person"])
        self.combo_bg = make_combo(dp.BACKGROUNDS)

        lbl_style = f"color: {C['text_dim']}; font-size: 10px; letter-spacing: 1px;"
        for label, widget in [
            ("Mood", self.combo_mood),
            ("Build", self.combo_body),
            ("Age", self.combo_age),
            ("Gender", self.combo_gender),
            ("Background", self.combo_bg),
        ]:
            lbl = QLabel(label)
            lbl.setStyleSheet(lbl_style)
            flay.addRow(lbl, widget)

        lay.addLayout(flay)

        # ── CLAUDE ANALYSIS ──
        lay.addWidget(section_label("▶ Claude Analysis"))
        self.chk_auto_analyse = QCheckBox("Auto-analyse every generation")
        self.chk_auto_analyse.setChecked(True)
        self.chk_auto_analyse.setStyleSheet(f"color: {C['text_dim']}; font-size: 11px;")
        lay.addWidget(self.chk_auto_analyse)

        lay.addWidget(hline())

        # ── BUTTONS ──
        btn_lay = QHBoxLayout()
        self.btn_generate = QPushButton("CLAUDE GEN")
        self.btn_generate.setObjectName("btn_generate")
        self.btn_local = QPushButton("LOCAL")
        self.btn_local.setObjectName("btn_random")
        self.btn_local.setToolTip("Generate from pools directly (fast, offline fallback)")
        self.btn_random = QPushButton("↻ RANDOM")
        self.btn_random.setObjectName("btn_random")
        btn_lay.addWidget(self.btn_generate)
        btn_lay.addWidget(self.btn_local)
        btn_lay.addWidget(self.btn_random)
        lay.addLayout(btn_lay)

        btn_lay2 = QHBoxLayout()
        self.btn_copy = QPushButton("COPY PROMPT")
        self.btn_copy.setObjectName("btn_copy")
        self.btn_clear = QPushButton("CLEAR")
        btn_lay2.addWidget(self.btn_copy)
        btn_lay2.addWidget(self.btn_clear)
        lay.addLayout(btn_lay2)

        lay.addStretch()

        # ── STATS FOOTER ──
        self.lbl_stats = QLabel("No history yet")
        self.lbl_stats.setStyleSheet(f"color: {C['muted']}; font-size: 10px;")
        self.lbl_stats.setWordWrap(True)
        lay.addWidget(self.lbl_stats)

        self.btn_generate.clicked.connect(self.generate)
        self.btn_local.clicked.connect(self.generate_local)
        self.btn_random.clicked.connect(self.generate_random)
        self.btn_copy.clicked.connect(self.copy_prompt)
        self.btn_clear.clicked.connect(self.clear)

        scroll.setWidget(w)
        return outer

    def _build_main(self) -> QWidget:
        tabs = QTabWidget()

        # ── TAB: PROMPT ──
        tab_prompt = QWidget()
        lay = QVBoxLayout(tab_prompt)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)

        # Character card
        self.char_card = QFrame()
        self.char_card.setStyleSheet(f"background: {C['panel2']}; border: 1px solid {C['border']};")
        card_lay = QHBoxLayout(self.char_card)
        card_lay.setContentsMargins(12, 10, 12, 10)
        self.lbl_char_info = QLabel("— no character generated yet —")
        self.lbl_char_info.setStyleSheet(f"color: {C['muted']}; font-size: 11px; border: none;")
        self.lbl_char_info.setWordWrap(True)
        card_lay.addWidget(self.lbl_char_info)
        self.char_card.setMaximumHeight(100)
        lay.addWidget(self.char_card)

        # Prompt output
        self.prompt_output = QTextEdit()
        self.prompt_output.setReadOnly(False)
        self.prompt_output.setPlaceholderText(
            "// Prompt will appear here after generation.\n"
            "// You can also edit it manually before analysing."
        )
        self.prompt_output.setMinimumHeight(200)
        self.prompt_output.setStyleSheet(f"""
            QTextEdit {{
                background: {C['bg']};
                border: 1px solid {C['border']};
                color: {C['text']};
                font-family: "IBM Plex Mono", "Courier New", monospace;
                font-size: 12px;
                line-height: 1.6;
                padding: 12px;
            }}
        """)
        self._highlighter = PromptHighlighter(self.prompt_output.document())
        lay.addWidget(self.prompt_output, stretch=2)

        # Analyse button row
        analyse_row = QHBoxLayout()
        self.btn_analyse = QPushButton("SEND TO CLAUDE →")
        self.btn_analyse.setObjectName("btn_iterate")
        self.btn_analyse.setEnabled(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        analyse_row.addWidget(self.btn_analyse)
        analyse_row.addWidget(self.progress_bar)
        lay.addLayout(analyse_row)

        self.btn_analyse.clicked.connect(self.send_to_claude)
        tabs.addTab(tab_prompt, "PROMPT")

        # ── TAB: CLAUDE ──
        tab_claude = QWidget()
        clay = QVBoxLayout(tab_claude)
        clay.setContentsMargins(16, 16, 16, 16)
        clay.setSpacing(10)

        # Score row
        score_row = QHBoxLayout()
        self.lbl_claude_score = QLabel("—")
        self.lbl_claude_score.setObjectName("score_label")
        self.lbl_claude_score.setFixedWidth(50)
        score_row.addWidget(QLabel("CLAUDE SCORE:"))
        score_row.addWidget(self.lbl_claude_score)
        score_row.addWidget(QLabel("   YOUR OVERRIDE:"))

        self.slider_user_score = QSlider(Qt.Orientation.Horizontal)
        self.slider_user_score.setRange(0, 10)
        self.slider_user_score.setValue(0)
        self.slider_user_score.setFixedWidth(160)
        self.lbl_user_score_val = QLabel("—")
        self.lbl_user_score_val.setStyleSheet(
            f"color: {C['amber']}; font-size: 16px; font-weight: bold;"
        )
        score_row.addWidget(self.slider_user_score)
        score_row.addWidget(self.lbl_user_score_val)
        self.btn_submit_score = QPushButton("SUBMIT")
        self.btn_submit_score.setEnabled(False)
        score_row.addWidget(self.btn_submit_score)
        score_row.addStretch()
        clay.addLayout(score_row)

        self.slider_user_score.valueChanged.connect(self._on_slider_change)
        self.btn_submit_score.clicked.connect(self._submit_user_score)

        # Weaknesses
        self.weakness_row = QHBoxLayout()
        self.weakness_row.setSpacing(6)
        clay.addLayout(self.weakness_row)

        # Reasoning
        clay.addWidget(section_label("▶ Claude Reasoning"))
        self.txt_reasoning = QTextEdit()
        self.txt_reasoning.setReadOnly(True)
        self.txt_reasoning.setMaximumHeight(100)
        self.txt_reasoning.setStyleSheet(
            f"background: {C['panel2']}; border: 1px solid {C['border']}; "
            f"color: {C['text_dim']}; font-size: 11px;"
        )
        clay.addWidget(self.txt_reasoning)

        # Refined prompt
        clay.addWidget(section_label("▶ Refined Prompt"))
        self.txt_refined = QTextEdit()
        self.txt_refined.setReadOnly(False)
        self.txt_refined.setStyleSheet(
            f"background: {C['bg']}; border: 1px solid {C['border']}; "
            f"color: {C['text']}; font-size: 12px; padding: 10px;"
        )
        self._highlighter2 = PromptHighlighter(self.txt_refined.document())
        clay.addWidget(self.txt_refined, stretch=2)

        # Next suggestion
        self.lbl_suggestion = QLabel("")
        self.lbl_suggestion.setStyleSheet(
            f"color: {C['teal_b']}; font-size: 11px; font-style: italic;"
        )
        self.lbl_suggestion.setWordWrap(True)
        clay.addWidget(self.lbl_suggestion)

        # Iterate row
        iter_row = QHBoxLayout()
        self.input_iterate = QLineEdit()
        self.input_iterate.setPlaceholderText(
            "Tell Claude what to push / change / explore next..."
        )
        self.btn_iterate = QPushButton("ITERATE →")
        self.btn_iterate.setObjectName("btn_iterate")
        self.btn_iterate.setEnabled(False)
        iter_row.addWidget(self.input_iterate)
        iter_row.addWidget(self.btn_iterate)
        clay.addLayout(iter_row)
        self.btn_iterate.clicked.connect(self._iterate)

        # Accept / copy refined
        accept_row = QHBoxLayout()
        self.btn_accept_refined = QPushButton("← USE REFINED PROMPT")
        self.btn_accept_refined.setObjectName("btn_copy")
        self.btn_accept_refined.setEnabled(False)
        self.btn_copy_refined = QPushButton("COPY REFINED")
        self.btn_copy_refined.setObjectName("btn_copy")
        self.btn_copy_refined.setEnabled(False)
        accept_row.addWidget(self.btn_accept_refined)
        accept_row.addWidget(self.btn_copy_refined)
        accept_row.addStretch()
        clay.addLayout(accept_row)

        self.btn_accept_refined.clicked.connect(self._accept_refined)
        self.btn_copy_refined.clicked.connect(self._copy_refined)

        tabs.addTab(tab_claude, "CLAUDE")

        # ── TAB: HISTORY ──
        tab_hist = QWidget()
        hlay = QVBoxLayout(tab_hist)
        hlay.setContentsMargins(16, 16, 16, 16)
        hlay.setSpacing(8)
        hlay.addWidget(section_label("▶ Generation History"))
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("font-size: 11px;")
        hlay.addWidget(self.history_list, stretch=1)
        self.history_list.itemClicked.connect(self._load_history_item)

        btn_row_h = QHBoxLayout()
        btn_clear_hist = QPushButton("CLEAR HISTORY")
        btn_clear_hist.clicked.connect(self._clear_history)
        btn_row_h.addWidget(btn_clear_hist)
        btn_row_h.addStretch()
        hlay.addLayout(btn_row_h)

        tabs.addTab(tab_hist, "HISTORY")

        # ── TAB: STATS ──
        tab_stats = QWidget()
        slay = QVBoxLayout(tab_stats)
        slay.setContentsMargins(16, 16, 16, 16)
        slay.setSpacing(8)
        slay.addWidget(section_label("▶ Learning Stats"))
        self.txt_stats = QTextEdit()
        self.txt_stats.setReadOnly(True)
        self.txt_stats.setStyleSheet(
            f"background: {C['panel2']}; border: 1px solid {C['border']}; "
            f"color: {C['text_dim']}; font-size: 11px;"
        )
        slay.addWidget(self.txt_stats)
        btn_refresh_stats = QPushButton("REFRESH STATS")
        btn_refresh_stats.clicked.connect(self._refresh_stats)
        slay.addWidget(btn_refresh_stats)

        tabs.addTab(tab_stats, "STATS")

        self.tabs = tabs
        return tabs

    # ── SHORTCUTS ─────────────────────────────────────────────────────────────
    def _setup_shortcuts(self):
        QShortcut(QKeySequence("F5"), self).activated.connect(self.generate)
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(self.generate)
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self.copy_prompt)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self).activated.connect(self.generate_random)

    # ── GENERATION ────────────────────────────────────────────────────────────
    def _get_archetype_key(self) -> str:
        idx = self.combo_archetype.currentIndex()
        keys = ["random"] + list(dp.ARCHETYPES.keys())
        return keys[idx] if idx < len(keys) else "random"

    def _get_overrides(self) -> dict:
        ov = {}
        if self.input_name.text().strip():
            ov["name"] = self.input_name.text().strip()
        if self.input_role.text().strip():
            ov["role"] = self.input_role.text().strip()
        if self.input_personality.text().strip():
            ov["personality"] = self.input_personality.text().strip()
        if self.input_extra.toPlainText().strip():
            ov["extra"] = self.input_extra.toPlainText().strip()
        if self.combo_mood.currentIndex() > 0:
            ov["mood"] = self.combo_mood.currentText()
        if self.combo_body.currentIndex() > 0:
            ov["body_type"] = self.combo_body.currentText()
        if self.combo_age.currentIndex() > 0:
            ov["age"] = self.combo_age.currentText()
        if self.combo_gender.currentIndex() > 0:
            ov["gender"] = self.combo_gender.currentText()
        if self.combo_bg.currentIndex() > 0:
            ov["background"] = self.combo_bg.currentText()
        return ov

    def generate(self):
        """Claude generation path — pools as vocabulary reference, Claude invents freely."""
        archetype_key = self._get_archetype_key()
        if archetype_key == "random":
            import random
            archetype_key = random.choice(list(dp.ARCHETYPES.keys()))

        arch = dp.ARCHETYPES[archetype_key]
        overrides = self._get_overrides()
        vocabulary = dp.get_archetype_vocabulary(archetype_key)

        self._current_entry_id = str(uuid.uuid4())[:8]
        self._claude_result = None
        self._reset_claude_panel()
        self.btn_analyse.setEnabled(False)
        self.progress_bar.show()
        self.status("Claude generating character...")

        claude_worker.generate_character_async(
            archetype_key=archetype_key,
            archetype_label=arch["label"],
            palette_hint=arch["palette_hint"],
            style_flex=arch["style_flex"],
            overrides=overrides,
            archetype_vocabulary=vocabulary,
            on_complete=lambda char: self.claude_generated.emit(char),
            on_error=lambda err: self.claude_generate_error.emit(err),
        )

    def _on_claude_generated(self, char: dict):
        """Receive Claude-generated character, build prompt, update UI."""
        prompt = char.get("assembled_prompt") or dp.assemble_prompt(char)
        self._current_char = char
        self._current_prompt = prompt

        self.prompt_output.setPlainText(prompt)
        self._update_char_card(char)
        self.btn_analyse.setEnabled(True)
        self.progress_bar.hide()
        self._update_stats_footer()
        self.tabs.setCurrentIndex(0)
        self.status(f"Claude generated: {char['archetype_label']} / {char.get('role', '')[:40]}")

        if self.chk_auto_analyse.isChecked():
            QTimer.singleShot(300, self.send_to_claude)

    def _on_claude_generate_error(self, error: str):
        self.progress_bar.hide()
        self.btn_analyse.setEnabled(False)
        self.status(f"Claude generation error: {error[:80]} — try LOCAL instead")

    def generate_local(self):
        """Local fallback path — direct pool selection, fast and offline."""
        weights = learning.get_weights()
        char = dp.build_character(
            archetype_key=self._get_archetype_key(),
            overrides=self._get_overrides(),
            combo_weights=weights,
        )
        prompt = dp.assemble_prompt(char)
        self._current_char = char
        self._current_entry_id = str(uuid.uuid4())[:8]
        self._current_prompt = prompt
        self._claude_result = None

        self.prompt_output.setPlainText(prompt)
        self._update_char_card(char)
        self.btn_analyse.setEnabled(True)
        self._reset_claude_panel()
        self._update_stats_footer()

        self.tabs.setCurrentIndex(0)
        self.status(f"[LOCAL] Generated: {char['archetype_label']} / {char['role'][:40]}")

        if self.chk_auto_analyse.isChecked():
            QTimer.singleShot(300, self.send_to_claude)

    def generate_random(self):
        """Full random — clears all overrides and fires Claude generation."""
        self.combo_archetype.setCurrentIndex(0)
        self.combo_mood.setCurrentIndex(0)
        self.combo_body.setCurrentIndex(0)
        self.combo_age.setCurrentIndex(0)
        self.combo_gender.setCurrentIndex(0)
        self.combo_bg.setCurrentIndex(0)
        self.input_name.clear()
        self.input_role.clear()
        self.input_personality.clear()
        self.input_extra.clear()
        self.generate()

    def _update_char_card(self, char: dict):
        era = char.get("era_blend", "")
        era_span = (
            f"<br><span style='color:{C['teal_b']}; font-size:10px;'>{era}</span>"
            if era else ""
        )
        lines = [
            f"<b style='color:{C['amber']}'>{char['archetype_label'].upper()}</b>  "
            f"<span style='color:{C['text_dim']}'>{'| ' + char['name'] if char['name'] else ''}</span>",
            f"<span style='color:{C['green_b']}'>{char.get('role','')}</span>"
            f"  <span style='color:{C['muted']}'>({char.get('age','').split('—')[0].strip()})</span>"
            f"{era_span}",
            f"<span style='color:{C['text_dim']}'>{char.get('personality','')}</span>",
        ]
        self.lbl_char_info.setText("<br>".join(lines))
        self.lbl_char_info.setTextFormat(Qt.TextFormat.RichText)

    # ── CLAUDE ────────────────────────────────────────────────────────────────
    def send_to_claude(self):
        if not self._current_entry_id:
            return
        prompt_text = self.prompt_output.toPlainText().strip()
        if not prompt_text:
            return

        self.progress_bar.show()
        self.btn_analyse.setEnabled(False)
        self.btn_iterate.setEnabled(False)
        self._pending_analysis = True
        self.status("Claude analysing...")

        claude_worker.analyse_prompt_async(
            entry_id=self._current_entry_id,
            prompt=prompt_text,
            on_complete=lambda eid, res: self.claude_done.emit(eid, res),
            on_error=lambda eid, err: self.claude_error.emit(eid, err),
        )

    def _iterate(self):
        if not self._current_entry_id:
            return
        feedback = self.input_iterate.text().strip()
        if not feedback:
            return
        self.progress_bar.show()
        self.btn_iterate.setEnabled(False)
        self.status("Claude iterating...")
        claude_worker.iterate_refinement_async(
            entry_id=self._current_entry_id,
            user_feedback=feedback,
            on_complete=lambda eid, res: self.claude_done.emit(eid, res),
            on_error=lambda eid, err: self.claude_error.emit(eid, err),
        )

    def _on_claude_done(self, entry_id: str, result: dict):
        self.progress_bar.hide()
        self.btn_analyse.setEnabled(True)
        self.btn_iterate.setEnabled(True)
        self._pending_analysis = False
        self._claude_result = result

        score = result.get("score", 0)
        reasoning = result.get("reasoning", "")
        weaknesses = result.get("weaknesses", [])
        refined = result.get("refined_prompt", "")
        suggestion = result.get("next_iteration_suggestion", "")

        color = C["green_b"] if score >= 7 else C["amber"] if score >= 5 else C["red"]
        self.lbl_claude_score.setText(f"{score:.1f}")
        self.lbl_claude_score.setStyleSheet(
            f"color: {color}; font-size: 22px; font-weight: bold;"
        )

        self.txt_reasoning.setPlainText(reasoning)

        while self.weakness_row.count():
            item = self.weakness_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for w in weaknesses[:6]:
            tag = QLabel(w)
            tag.setObjectName("weakness_tag")
            self.weakness_row.addWidget(tag)
        self.weakness_row.addStretch()

        self.txt_refined.setPlainText(refined)
        self.lbl_suggestion.setText(f"→ {suggestion}")

        self.btn_accept_refined.setEnabled(bool(refined))
        self.btn_copy_refined.setEnabled(bool(refined))
        self.btn_submit_score.setEnabled(True)
        self.slider_user_score.setValue(0)
        self.lbl_user_score_val.setText("—")

        if self._current_char:
            learning.record_entry(
                char=self._current_char,
                prompt=self.prompt_output.toPlainText(),
                claude_score=score,
                claude_reasoning=reasoning,
                claude_refined_prompt=refined,
                weaknesses=weaknesses,
                user_score=None,
            )
            self._refresh_history()

        self.tabs.setCurrentIndex(1)
        self.status(f"Claude scored: {score:.1f}/10  |  {len(weaknesses)} weaknesses flagged")

    def _on_claude_error(self, entry_id: str, error: str):
        self.progress_bar.hide()
        self.btn_analyse.setEnabled(True)
        self.btn_iterate.setEnabled(True)
        self._pending_analysis = False
        self.status(f"Claude error: {error[:80]}")

    def _reset_claude_panel(self):
        self.lbl_claude_score.setText("—")
        self.lbl_claude_score.setStyleSheet(
            f"color: {C['muted']}; font-size: 22px; font-weight: bold;"
        )
        self.txt_reasoning.clear()
        self.txt_refined.clear()
        self.lbl_suggestion.setText("")
        self.btn_accept_refined.setEnabled(False)
        self.btn_copy_refined.setEnabled(False)
        self.btn_iterate.setEnabled(False)
        self.btn_submit_score.setEnabled(False)
        while self.weakness_row.count():
            item = self.weakness_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # ── SCORING ───────────────────────────────────────────────────────────────
    def _on_slider_change(self, val: int):
        self.lbl_user_score_val.setText("—" if val == 0 else str(val))

    def _submit_user_score(self):
        val = self.slider_user_score.value()
        if val == 0 or not self._current_entry_id:
            return
        learning.update_user_score(self._current_entry_id, float(val))
        self.btn_submit_score.setEnabled(False)
        self.status(f"User score {val}/10 saved — learning updated")
        self._update_stats_footer()

    # ── ACTIONS ───────────────────────────────────────────────────────────────
    def copy_prompt(self):
        txt = self.prompt_output.toPlainText()
        if txt:
            QApplication.clipboard().setText(txt)
            self.status("Prompt copied to clipboard")

    def _copy_refined(self):
        txt = self.txt_refined.toPlainText()
        if txt:
            QApplication.clipboard().setText(txt)
            self.status("Refined prompt copied")

    def _accept_refined(self):
        txt = self.txt_refined.toPlainText()
        if txt:
            self.prompt_output.setPlainText(txt)
            self.tabs.setCurrentIndex(0)
            self.status("Refined prompt loaded into editor")

    def clear(self):
        self.prompt_output.clear()
        self._current_char = None
        self._current_entry_id = None
        self._current_prompt = ""
        self._claude_result = None
        self.lbl_char_info.setText("— no character generated yet —")
        self.btn_analyse.setEnabled(False)
        self._reset_claude_panel()
        self.status("Cleared")

    # ── HISTORY ───────────────────────────────────────────────────────────────
    def _refresh_history(self):
        self.history_list.clear()
        entries = learning.get_history(50)
        for e in entries:
            char = e.get("char_snapshot", {})
            cs = e.get("claude_score") or 0
            us = e.get("user_score")
            score_str = f"C:{cs:.1f}" + (f" U:{us:.0f}" if us else "")
            label = (
                f"[{e['id']}]  {char.get('archetype_label','?')[:20]:20}  "
                f"{char.get('role','?')[:30]:30}  {score_str}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, e)
            if us and us >= 7:
                item.setForeground(QColor(C["green_b"]))
            elif cs and cs < 5:
                item.setForeground(QColor(C["muted"]))
            self.history_list.addItem(item)

    def _load_history_item(self, item: QListWidgetItem):
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
        self.prompt_output.setPlainText(entry.get("original_prompt", ""))
        if entry.get("char_snapshot"):
            self._update_char_card(entry["char_snapshot"])
        if entry.get("refined_prompt"):
            self.txt_refined.setPlainText(entry["refined_prompt"])
        if entry.get("claude_reasoning"):
            self.txt_reasoning.setPlainText(entry["claude_reasoning"])
        cs = entry.get("claude_score")
        if cs:
            self.lbl_claude_score.setText(f"{cs:.1f}")
        self.status(f"Loaded history entry {entry['id']}")

    def _clear_history(self):
        reply = QMessageBox.question(
            self, "Clear History",
            "Clear all history and reset learning weights?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            learning.clear_history()
            self._refresh_history()
            self.status("History cleared")

    # ── STATS ─────────────────────────────────────────────────────────────────
    def _refresh_stats(self):
        stats = learning.get_stats()
        lines = [
            f"Total generated:    {stats.get('total_generated', 0)}",
            f"Total rated:        {stats.get('total_rated', 0)}",
            f"Avg Claude score:   {stats.get('avg_claude_score') or '—'}",
            f"Avg user score:     {stats.get('avg_user_score') or '—'}",
            f"Score disagreements:{stats.get('disagreements', 0)}",
            "",
            "── TOP WEAKNESS FLAGS ──",
        ]
        for tag, count in stats.get("top_weaknesses", []):
            lines.append(f"  {count:3}×  {tag}")
        lines += ["", "── HIGHEST SCORING COMBOS ──"]
        for item, score in stats.get("top_combos", [])[:10]:
            lines.append(f"  {score:.1f}  {item[:55]}")
        lines += ["", "── LOWEST SCORING COMBOS ──"]
        for item, score in stats.get("worst_combos", [])[:5]:
            lines.append(f"  {score:.1f}  {item[:55]}")
        self.txt_stats.setPlainText("\n".join(lines))

    def _update_stats_footer(self):
        stats = learning.get_stats()
        n = stats.get("total_generated", 0)
        avg = stats.get("avg_user_score") or stats.get("avg_claude_score")
        self.lbl_stats.setText(f"{n} generated  |  avg score: {avg or '—'}")

    # ── STATUS ────────────────────────────────────────────────────────────────
    def status(self, msg: str):
        self.statusBar().showMessage(f"  {msg}")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Devoted Absurd")
    QFontDatabase.addApplicationFont(":/fonts/IBMPlexMono.ttf")
    win = MainWindow()
    win.show()
    win._refresh_history()
    win._update_stats_footer()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
