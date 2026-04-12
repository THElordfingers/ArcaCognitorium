# Departamentum Documentalis · opening_ceremony.py · v1.1
from PyQt6.QtWidgets import QSplashScreen
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont

LOADING_TEXTS = [
    "Consulting the Decree Table...",
    "Ratifying field schemas...",
    "Verifying the mandate has not changed since you last checked...",
    "Interrogating SQLite WAL...",
    "Preparing the forms to receive the forms...",
    "Confirming that nothing has been deleted...",
    "Summoning the Tabularium Renderer...",
    "The Devoted Absurd proceeds regardless...",
]

class OpeningCeremony(QSplashScreen):
    def __init__(self, on_complete):
        px = QPixmap(640, 380)
        px.fill(QColor("#050507"))
        super().__init__(px, Qt.WindowType.WindowStaysOnTopHint)
        self._on_complete = on_complete
        self._title = "DEPARTAMENTUM DOCUMENTALIS"
        self._displayed = ""
        self._progress = 0
        self._loading_idx = 0
        self._char_timer = QTimer(self)
        self._char_timer.timeout.connect(self._next_char)
        self._char_timer.start(80)

    def _next_char(self):
        if len(self._displayed) < len(self._title):
            self._displayed += self._title[len(self._displayed)]
            ratio = len(self._displayed) / len(self._title)
            self._progress = int(ratio * 60)
            self._loading_idx = min(int(ratio * len(LOADING_TEXTS)), len(LOADING_TEXTS) - 1)
            self.repaint()
        else:
            self._char_timer.stop()
            t = QTimer(self); t.setSingleShot(True)
            t.timeout.connect(self._finalise)
            t.start(400)

    def _finalise(self):
        self._progress = 100
        self.repaint()
        QTimer.singleShot(200, self._on_complete)

    def drawContents(self, painter: QPainter):
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, QColor("#050507"))

        painter.setFont(QFont("Georgia", 18, QFont.Weight.Bold))
        painter.setPen(QColor("#d4af37"))
        painter.drawText(0, 80, w, 40, Qt.AlignmentFlag.AlignHCenter, self._displayed)

        painter.setFont(QFont("Georgia", 9))
        painter.setPen(QColor("#c8b88a"))
        painter.drawText(0, 120, w, 25, Qt.AlignmentFlag.AlignHCenter,
                         "Department of Documented Design Definitives")
        painter.drawText(0, 140, w, 25, Qt.AlignmentFlag.AlignHCenter,
                         "Define! Designa! Denota! Discede!")

        painter.setFont(QFont("Courier Prime", 8))
        painter.setPen(QColor("#555566"))
        txt = LOADING_TEXTS[self._loading_idx] if self._loading_idx < len(LOADING_TEXTS) else ""
        painter.drawText(0, 200, w, 20, Qt.AlignmentFlag.AlignHCenter, txt)

        bar_w = int(w * 0.7)
        bar_x = (w - bar_w) // 2
        painter.setPen(QColor("#2a2a3a"))
        painter.setBrush(QColor("#0a0a12"))
        painter.drawRect(bar_x, 240, bar_w, 8)
        fill = int(bar_w * self._progress / 100)
        painter.setBrush(QColor("#d4af37"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(bar_x, 240, fill, 8)
