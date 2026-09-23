DARK_STYLE = """
QWidget { background: #0b1020; color: #f8fafc; font-family: 'Segoe UI'; font-size: 13px; }
QMainWindow { background: #0b1020; }
QLabel#eyebrow { color: #7f9cf5; font-size: 11px; font-weight: 700; letter-spacing: 1px; }
QLabel#pageTitle { font-size: 28px; font-weight: 700; }
QLabel#pageSubtitle { color: #94a3b8; font-size: 14px; }
QFrame#topBar, QFrame#sidebar, QFrame#card, QFrame#panel { background: #111827; border: 1px solid #263247; border-radius: 12px; }
QFrame#sidebar { border-radius: 0px; border-top: 0px; border-bottom: 0px; border-left: 0px; }
QPushButton { background: #1b2942; color: #f8fafc; border: 1px solid #31415e; border-radius: 8px; padding: 9px 14px; font-weight: 600; }
QPushButton:hover { background: #263b63; border-color: #5b8cff; }
QPushButton:pressed { background: #152443; }
QPushButton:disabled { color: #64748b; background: #111827; }
QPushButton#accent { background: #5b8cff; border-color: #5b8cff; color: white; }
QPushButton#accent:hover { background: #739cff; }
QPushButton#nav { text-align: left; border: 0px; background: transparent; color: #94a3b8; padding: 11px 16px; }
QPushButton#nav:hover { background: #18243a; color: #f8fafc; }
QPushButton#nav[active="true"] { background: #1d3158; color: #dbe7ff; border-left: 3px solid #5b8cff; }
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox { background: #0b1020; border: 1px solid #263247; border-radius: 8px; padding: 9px; color: #f8fafc; selection-background-color: #315aa8; }
QComboBox QAbstractItemView { background: #111827; color: #f8fafc; selection-background-color: #315aa8; }
QGroupBox { border: 1px solid #263247; border-radius: 10px; margin-top: 14px; padding: 16px; font-weight: 700; }
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 5px; color: #dbe7ff; }
QTableWidget { background: #111827; border: 1px solid #263247; gridline-color: #263247; border-radius: 8px; }
QHeaderView::section { background: #18243a; color: #cbd5e1; border: 0px; padding: 8px; font-weight: 700; }
QProgressBar { background: #0b1020; border: 1px solid #263247; border-radius: 6px; text-align: center; height: 12px; }
QProgressBar::chunk { background: #5b8cff; border-radius: 5px; }
QScrollBar:vertical { background: #0b1020; width: 10px; }
QScrollBar::handle:vertical { background: #31415e; border-radius: 5px; min-height: 30px; }
"""
