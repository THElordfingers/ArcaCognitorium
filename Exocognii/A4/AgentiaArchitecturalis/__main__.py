"""
Agentia Architecturalis — Bureau II Entry Point

Usage: python -m AgentiaArchitecturalis
"""
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow
from .opening_ceremony import OpeningCeremony
from .auxilium import AuxiliumFeature
from .features.tabula.tabula_feature import TabulaFeature
from .features.specularium.preview_data_model import PreviewDataModel
from .features.specularium.specularium_feature import SpeculariumFeature
from .features.specularium.specularium_window import SpeculariumWindow
from .features.codex_exportum.codex_feature import CodexFeature
from .features.armarium.armarium_feature import ArmariumFeature
from .features.thema.thema_feature import ThemaFeature


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Agentia Architecturalis")
    app.setOrganizationName("Triumviratus Aestheticus Imperialis")

    window = MainWindow()

    # ── Wire features ───────────────────────────────────────────

    # Tabula
    tabula = TabulaFeature()
    window.set_feature_page("tabula", tabula)
    tabula.canvas_name_changed.connect(window.titulum.set_canvas_name)
    tabula.canvas_name_changed.connect(window.fascia.set_canvas_name)
    tabula.dirty_changed.connect(window.titulum.set_dirty)
    tabula.element_count_changed.connect(
        lambda n: window.set_status(right=f"{tabula.session.current_name or '(untitled)'} \u00b7 {n} elms")
    )

    # Fascia → Tabula signals
    window.fascia.new_canvas.connect(tabula.new_canvas)
    window.fascia.open_canvas.connect(tabula.open_canvas)
    window.fascia.save_canvas.connect(tabula.save_canvas)
    window.fascia.save_canvas_as.connect(tabula.save_canvas_as)
    window.fascia.undo.connect(tabula.canvas.undo)
    window.fascia.redo.connect(tabula.canvas.redo)
    window.fascia.delete_element.connect(tabula.canvas.delete_selected)
    window.fascia.duplicate_element.connect(tabula.canvas.duplicate_selected)
    window.fascia.group_element.connect(tabula.canvas.group_selected)

    # Specularium (dual-instance shared data model)
    preview_model = PreviewDataModel()
    specularium = SpeculariumFeature(preview_model)
    specularium_window = SpeculariumWindow(preview_model)
    window.set_feature_page("specularium", specularium)

    # Canvas changes → PreviewDataModel
    tabula.design_changed.connect(
        lambda: preview_model.update_design(tabula.canvas.serialize_all())
    )

    # Fascia → Specularium
    window.fascia.reconstruct.connect(
        lambda: preview_model.update_design(tabula.canvas.serialize_all())
    )
    window.fascia.toggle_window.connect(specularium_window.toggle)

    # Codex Exportum
    codex = CodexFeature()
    window.set_feature_page("codex", codex)

    # Update codex when switching to it
    def _update_codex():
        codex.update_source(
            tabula.session.current_name or "untitled",
            tabula.canvas.serialize_all(),
        )
    window.feature_codex.feature_selected.connect(
        lambda key: _update_codex() if key == "codex" else None
    )
    window.fascia.copy_to_clipboard.connect(codex.copy_to_clipboard)
    window.fascia.save_to_file.connect(codex.save_to_file)
    window.fascia.validate_code.connect(codex.validate_current)

    # Armarium
    armarium = ArmariumFeature()
    window.set_feature_page("armarium", armarium)

    import json as _json
    window.fascia.seal_canvas.connect(
        lambda: armarium.seal_canvas(
            _json.dumps([e.to_dict() for e in tabula.canvas.serialize_all()]),
            window.theme_manager.theme_name,
        )
    )
    window.fascia.export_selected.connect(armarium.export_selected)

    # Thema
    thema = ThemaFeature(window.theme_manager)
    window.set_feature_page("thema", thema)

    window.fascia.load_theme.connect(thema.load_theme)
    window.fascia.apply_repaint.connect(thema.apply_and_repaint)
    window.fascia.reset_theme.connect(thema.reset_theme)

    thema.theme_applied.connect(lambda tok: (
        tabula.canvas.refresh_tokens(tok),
        preview_model.refresh_tokens(tok),
        window.titulum.set_theme_name(window.theme_manager.theme_name),
        app.setStyleSheet(window.theme_manager.build_qss()),
    ))
    thema.theme_reset.connect(lambda: (
        tabula.canvas.refresh_tokens(window.theme_manager.active_tokens),
        preview_model.refresh_tokens(window.theme_manager.active_tokens),
        window.titulum.set_theme_name("Nox Aurum"),
        app.setStyleSheet(window.theme_manager.build_qss()),
    ))

    # Auxilium
    auxilium = AuxiliumFeature()
    window.set_feature_page("auxilium", auxilium)

    # Update help content when feature changes
    window.feature_codex.feature_selected.connect(auxilium.set_feature)

    # ── Keyboard Shortcuts ──────────────────────────────────────
    from PyQt6.QtGui import QShortcut, QKeySequence
    QShortcut(QKeySequence("Ctrl+N"), window, tabula.new_canvas)
    QShortcut(QKeySequence("Ctrl+O"), window, tabula.open_canvas)
    QShortcut(QKeySequence("Ctrl+S"), window, tabula.save_canvas)
    QShortcut(QKeySequence("Ctrl+Shift+S"), window, tabula.save_canvas_as)
    QShortcut(QKeySequence("Ctrl+Z"), window, tabula.canvas.undo)
    QShortcut(QKeySequence("Ctrl+Shift+Z"), window, tabula.canvas.redo)
    QShortcut(QKeySequence("Delete"), window, tabula.canvas.delete_selected)
    QShortcut(QKeySequence("Ctrl+D"), window, tabula.canvas.duplicate_selected)
    QShortcut(QKeySequence("Ctrl+G"), window, tabula.canvas.group_selected)
    QShortcut(QKeySequence("Ctrl+P"), window, specularium_window.toggle)
    QShortcut(QKeySequence("F1"), window, lambda: window._on_feature_selected("auxilium"))

    # ── Apply theme ─────────────────────────────────────────────
    app.setStyleSheet(window.theme_manager.build_qss())

    # ── Opening Ceremony ────────────────────────────────────────
    if OpeningCeremony.should_show():
        ceremony = OpeningCeremony(window)
        ceremony.setGeometry(window.rect())
        ceremony.raise_()
        ceremony.show()
        ceremony.setFocus()

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
