#!/usr/bin/env python3
"""
🮈🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃🮃▍
🮈      PRAESIDIUM · widgets/art_widget.py                                          ▍
🭅▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃🭐
"""
# PRAESIDIUM · widgets/art_widget.py
# Image display widget. Supports PNG, JPEG, GIF, BMP, SVG, WEBP.
# Drag-and-drop. Fit/fill/actual size modes. Zoom +/-.
# version: 1.0.0

from pathlib import Path

from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QVBoxLayout, QFrame,
    QScrollArea, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QImageReader
from PyQt6.QtSvgWidgets import QSvgWidget

from widget_base import ArcaneWidget
from theme import (
    C_GOLD, C_GOLD_DIM, C_GOLD_DARK, C_TEXT, C_BG,
    arcane_button, micro_label,
)

SCALE_STEP = 0.15
SUPPORTED  = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".tif"}


class ArtWidget(ArcaneWidget):
    """
    Image display widget. Drop any image file to load it.
    Controls: fit to widget | actual size | zoom in/out.
    SVG rendered via QSvgWidget. All others via QPixmap.
    """

    image_loaded = pyqtSignal(str)   # path

    def __init__(self, widget_id: str, parent=None):
        super().__init__(widget_id, "Art", parent)
        self._path:   str | None = None
        self._pixmap: QPixmap | None = None
        self._scale   = 1.0
        self._is_svg  = False
        self._build_body()
        self.setAcceptDrops(True)
        self.set_status("idle", "Drop an image")

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------

    def _build_body(self) -> None:
        L = self._body_layout

        # Controls
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)

        self._btn_fit    = arcane_button("⊞ FIT")
        self._btn_actual = arcane_button("1:1")
        self._btn_zoom_in  = arcane_button("＋")
        self._btn_zoom_out = arcane_button("－")

        for btn in (self._btn_fit, self._btn_actual, self._btn_zoom_in, self._btn_zoom_out):
            btn.setFixedHeight(22)
            ctrl.addWidget(btn)

        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; font-size: 9px;"
        )
        ctrl.addStretch()
        ctrl.addWidget(self._info_lbl)
        L.addLayout(ctrl)
        L.addWidget(self._sep())

        # Scroll area contains the image label
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(False)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ border: none; background: {C_BG}; }}"
        )

        # SVG widget (shown for .svg files)
        self._svg_widget = QSvgWidget()
        self._svg_widget.setVisible(False)
        self._svg_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Pixmap label (shown for raster files)
        self._image_label = QLabel()
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._image_label.setStyleSheet(f"background: {C_BG};")
        self._image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        # Drop hint (shown when empty)
        self._drop_hint = QLabel("✦  Drop an image file here\n\nPNG · JPEG · GIF · SVG · BMP · WEBP")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint.setStyleSheet(
            f"color: {C_GOLD_DIM}; font-family: Georgia, serif; "
            "font-size: 10px; font-style: italic;"
        )

        self._scroll.setWidget(self._image_label)
        L.addWidget(self._drop_hint, 1)
        L.addWidget(self._scroll, 1)
        L.addWidget(self._svg_widget, 1)
        self._scroll.setVisible(False)

        # Wire
        self._btn_fit.clicked.connect(self._fit)
        self._btn_actual.clicked.connect(self._actual_size)
        self._btn_zoom_in.clicked.connect(lambda: self._zoom(1 + SCALE_STEP))
        self._btn_zoom_out.clicked.connect(lambda: self._zoom(1 - SCALE_STEP))

    def _sep(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet(f"color: {C_GOLD_DARK}; max-height: 1px;")
        return f

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load_image(self, path: str) -> None:
        p = Path(path)
        if p.suffix.lower() not in SUPPORTED:
            self.set_status("error", f"Unsupported: {p.suffix}")
            return

        self._path   = path
        self._is_svg = p.suffix.lower() == ".svg"

        self._drop_hint.setVisible(False)

        if self._is_svg:
            self._scroll.setVisible(False)
            self._svg_widget.setVisible(True)
            self._svg_widget.load(path)
            self.set_status("ok", p.name)
            self._info_lbl.setText(p.name)
        else:
            reader = QImageReader(path)
            reader.setAutoTransform(True)
            img = reader.read()
            if img.isNull():
                self.set_status("error", "Could not load image")
                return
            self._pixmap = QPixmap.fromImage(img)
            self._svg_widget.setVisible(False)
            self._scroll.setVisible(True)
            self._fit()
            size_str = f"{self._pixmap.width()}×{self._pixmap.height()}"
            self._info_lbl.setText(f"{p.name}  {size_str}")
            self.set_status("ok", p.name)

        self.image_loaded.emit(path)

    # ------------------------------------------------------------------
    # Scale controls
    # ------------------------------------------------------------------

    def _fit(self) -> None:
        if self._pixmap is None:
            return
        available = self._scroll.size()
        scaled = self._pixmap.scaled(
            available,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)
        self._image_label.resize(scaled.size())
        self._scale = scaled.width() / self._pixmap.width()

    def _actual_size(self) -> None:
        if self._pixmap is None:
            return
        self._image_label.setPixmap(self._pixmap)
        self._image_label.resize(self._pixmap.size())
        self._scale = 1.0

    def _zoom(self, factor: float) -> None:
        if self._pixmap is None:
            return
        self._scale = max(0.05, min(10.0, self._scale * factor))
        w = int(self._pixmap.width()  * self._scale)
        h = int(self._pixmap.height() * self._scale)
        scaled = self._pixmap.scaled(
            w, h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._image_label.setPixmap(scaled)
        self._image_label.resize(scaled.size())

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._pixmap and self._scale < 1.0:
            self._fit()

    # ------------------------------------------------------------------
    # Drag and drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and Path(urls[0].toLocalFile()).suffix.lower() in SUPPORTED:
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        urls = event.mimeData().urls()
        if urls:
            self.load_image(urls[0].toLocalFile())
