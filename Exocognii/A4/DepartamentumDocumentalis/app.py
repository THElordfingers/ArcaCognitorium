# Departamentum Documentalis · app.py · v1.2
from PyQt6.QtWidgets import QApplication, QMessageBox
import DepartamentumDocumentalis.db as db
from DepartamentumDocumentalis.styles import QSS
from DepartamentumDocumentalis import server

def launch(app: QApplication):
    app.setStyleSheet(QSS)
    db.init_schema()

    api_ok = server.start()
    if not api_ok:
        m = QMessageBox()
        m.setWindowTitle("Departamentum Documentalis")
        m.setText(
            "Port 8733 is already in use.\n\n"
            "Opening without FastAPI service.\n\n"
            "To free the port:  kill $(lsof -ti:8733)"
        )
        m.setIcon(QMessageBox.Icon.Warning)
        m.exec()

    from DepartamentumDocumentalis.main_window import MainWindow
    mw = MainWindow()
    mw.show()
