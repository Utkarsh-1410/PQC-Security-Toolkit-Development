from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class Card(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")


class MetricCard(Card):
    def __init__(self, label: str, value: str, detail: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        eyebrow = QLabel(label.upper())
        eyebrow.setObjectName("eyebrow")
        number = QLabel(value)
        number.setStyleSheet("font-size: 26px; font-weight: 700;")
        detail_label = QLabel(detail)
        detail_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(eyebrow); layout.addWidget(number); layout.addWidget(detail_label)


class Toast(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: #18243a; border: 1px solid #5b8cff; border-radius: 8px; padding: 10px 14px;")
        self.hide()

    def show_message(self, message: str, success: bool = True) -> None:
        self.setText(("✓ " if success else "✕ ") + message)
        self.show()
        QTimer.singleShot(3500, self.hide)


class NavButton(QPushButton):
    activated = Signal()

    def __init__(self, label: str, parent=None) -> None:
        super().__init__(label, parent)
        self.setObjectName("nav")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.activated)


from PySide6.QtCore import Qt
