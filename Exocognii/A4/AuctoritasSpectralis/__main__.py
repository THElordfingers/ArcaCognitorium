"""
AUCTORITAS SPECTRALIS — v1.0.0
Entry point: python3 -m AuctoritasSpectralis
from Exocognii/ parent directory with PYTHONPATH=.
"""

import sys
import os

def main():
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from AuctoritasSpectralis.app import AuctoritasSpectralisApp

    # High-DPI support
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("AuctoritasSpectralis")
    app.setApplicationDisplayName("AUCTORITAS SPECTRALIS")
    app.setApplicationVersion("1.0.0")

    window = AuctoritasSpectralisApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
