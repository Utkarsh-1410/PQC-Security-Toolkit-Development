from __future__ import annotations

import sys

from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PQC Security Toolkit")
    window = MainWindow()
    shortcuts = [("Ctrl+1", "dashboard"), ("Ctrl+2", "kem"), ("Ctrl+3", "signatures"), ("Ctrl+4", "files"), ("Ctrl+5", "benchmark"), ("Ctrl+6", "comparison"), ("Ctrl+,", "settings")]
    for sequence, page in shortcuts:
        action = QAction(window); action.setShortcut(QKeySequence(sequence)); action.triggered.connect(lambda checked=False, target=page: window.show_page(target)); window.addAction(action)
    quit_action = QAction(window); quit_action.setShortcut(QKeySequence("Ctrl+Q")); quit_action.triggered.connect(app.quit); window.addAction(quit_action)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
