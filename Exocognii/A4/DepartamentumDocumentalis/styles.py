# Departamentum Documentalis · styles.py · v1.1
QSS = """
QMainWindow, QWidget#root {
    background-color: #050507; color: #c8b88a;
    font-family: "Georgia"; font-size: 12px;
}
QWidget#left_rail {
    background-color: #0a0a12;
    border-right: 1px solid #1e1e2e;
    min-width: 220px; max-width: 220px;
}
QWidget#titulum {
    background-color: #050507;
    padding: 12px; border-bottom: 1px solid #1e1e2e;
}
QLabel#title_primary { color: #d4af37; font-family: "Georgia"; font-size: 11px; font-weight: bold; }
QLabel#title_sub     { color: #c8b88a; font-family: "Georgia"; font-size: 8px; }
QLabel#title_motto   { color: #555566; font-family: "Georgia"; font-size: 8px; font-style: italic; }
QPushButton#nav_button {
    background-color: transparent; color: #c8b88a;
    font-family: "Georgia"; font-size: 10px;
    text-align: left; padding: 6px 10px;
    border: none; border-bottom: 1px solid #0d0d18;
}
QPushButton#nav_button:hover  { background-color: #0d0d18; color: #d4af37; }
QPushButton#nav_button:checked {
    background-color: #12121f; color: #d4af37; border-left: 2px solid #d4af37;
}
QWidget#fascia {
    background-color: #0a0a12; border-bottom: 1px solid #1e1e2e;
    min-height: 52px; max-height: 52px;
}
QPushButton#fascia_button {
    background-color: #12121f; color: #c8b88a;
    font-family: "Courier Prime"; font-size: 9px;
    padding: 4px 12px; border: 1px solid #1e1e2e; border-radius: 2px;
}
QPushButton#fascia_button:hover { background-color: #1a1a2e; color: #d4af37; border-color: #d4af37; }
QPushButton#fascia_button_help {
    background-color: transparent; color: #555566;
    font-family: "Courier Prime"; font-size: 9px;
    padding: 4px 10px; border: 1px solid #2a2a3a; border-radius: 2px;
}
QPushButton#fascia_button_help:hover { color: #d4af37; border-color: #d4af37; }
QWidget#canvas { background-color: #050507; }
QLabel#dirty_marker { color: #d4af37; font-size: 10px; }
QLabel#badge_current      { background-color: #1a2a1a; color: #6abf69; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLabel#badge_versio_prior { background-color: #1e1e2e; color: #8888aa; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLabel#badge_archived     { background-color: #2a1a0a; color: #8b6913; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLabel#badge_orphaned     { background-color: #2a0a0a; color: #cc4444; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLabel#badge_mandated     { background-color: #1a2a1a; color: #6abf69; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLabel#badge_draft        { background-color: #1e1e2e; color: #8888aa; font-family: "Courier Prime"; font-size: 8px; padding: 2px 6px; border-radius: 2px; }
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0a0a12; color: #c8b88a;
    font-family: "Courier Prime"; font-size: 11px;
    border: 1px solid #1e1e2e; padding: 4px;
    selection-background-color: #d4af3733;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border: 1px solid #d4af37; }
QTextEdit#fixed_field_display {
    background-color: #070710; color: #555566;
    font-family: "Courier Prime"; font-style: italic; border: 1px solid #12121f;
}
QListWidget, QTableWidget {
    background-color: #0a0a12; color: #c8b88a;
    font-family: "Courier Prime"; font-size: 10px;
    border: 1px solid #1e1e2e; gridline-color: #1e1e2e;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #1a1a2e; color: #d4af37;
}
QHeaderView::section {
    background-color: #0a0a12; color: #555566;
    font-family: "Courier Prime"; font-size: 9px;
    border: none; border-bottom: 1px solid #1e1e2e; padding: 4px;
}
QScrollBar:vertical   { background: #050507; width: 8px; }
QScrollBar:horizontal { background: #050507; height: 8px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #1e1e2e; border-radius: 4px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background: #d4af37; }
QSplitter::handle       { background-color: #1e1e2e; }
QSplitter::handle:hover { background-color: #d4af37; }
QComboBox {
    background-color: #0a0a12; color: #c8b88a;
    border: 1px solid #1e1e2e;
    font-family: "Courier Prime"; font-size: 10px; padding: 2px 6px;
}
QComboBox QAbstractItemView {
    background-color: #0a0a12; color: #c8b88a; selection-background-color: #1a1a2e;
}
QPushButton {
    background-color: #12121f; color: #c8b88a;
    border: 1px solid #1e1e2e;
    font-family: "Courier Prime"; font-size: 10px;
    padding: 4px 10px; border-radius: 2px;
}
QPushButton:hover   { background-color: #1a1a2e; color: #d4af37; border-color: #d4af37; }
QPushButton:pressed { background-color: #0a0a12; }
QPushButton#btn_danger       { border-color: #cc4444; color: #cc4444; }
QPushButton#btn_danger:hover { background-color: #2a0a0a; }
"""
