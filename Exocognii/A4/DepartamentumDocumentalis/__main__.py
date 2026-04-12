# Departamentum Documentalis · __main__.py · v1.1
import sys
import warnings
warnings.filterwarnings("ignore", category=Warning, module="requests")

from PyQt6.QtWidgets import QApplication
from DepartamentumDocumentalis.app import launch

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DepartamentumDocumentalis")
    launch(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
