from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .widgets import Card


class Page(QWidget):
    def __init__(self, title: str, subtitle: str, parent=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(30, 26, 30, 30)
        self.layout.setSpacing(18)
        header = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("pageTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("pageSubtitle")
        subtitle_label.setWordWrap(True)
        header.addWidget(title_label); header.addWidget(subtitle_label)
        self.layout.addLayout(header)

    def section(self, title: str) -> Card:
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        label = QLabel(title.upper())
        label.setObjectName("eyebrow")
        card_layout.addWidget(label)
        return card

    @staticmethod
    def button(text: str, accent: bool = False) -> QPushButton:
        button = QPushButton(text)
        if accent:
            button.setObjectName("accent")
        return button

    @staticmethod
    def row(*widgets: QWidget) -> QHBoxLayout:
        layout = QHBoxLayout()
        for widget in widgets:
            layout.addWidget(widget)
        return layout
