from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel

from .page_base import Page
from .widgets import Card


class EducationPage(Page):
    def __init__(self, parent=None) -> None:
        super().__init__("Understanding Post-Quantum Cryptography", "A compact field guide to the algorithms and assumptions behind the toolkit.", parent)
        intro = self.section("Why PQC?"); text = QLabel("A sufficiently capable quantum computer could threaten widely deployed public-key systems. Post-quantum cryptography develops standardized algorithms designed to resist known classical and quantum attack strategies while remaining deployable on conventional hardware."); text.setWordWrap(True); intro.layout().addWidget(text); self.layout.addWidget(intro)
        grid = QGridLayout()
        for index, (name, purpose, family, operation) in enumerate([
            ("ML-KEM", "Key establishment", "Module lattice", "Encapsulation / decapsulation"),
            ("ML-DSA", "Digital signatures", "Module lattice", "Sign / verify"),
            ("SLH-DSA", "Digital signatures", "Hash based", "Sign / verify"),
            ("Classical systems", "Existing public-key cryptography", "Integer / elliptic curve", "Different security assumptions"),
        ]):
            card = Card(); layout = QGridLayout(); card.setLayout(layout); title = QLabel(name); title.setStyleSheet("font-size: 18px; font-weight: 700;"); body = QLabel(f"Purpose: {purpose}\nFamily: {family}\nPrimary operation: {operation}"); body.setStyleSheet("color: #94a3b8;"); layout.addWidget(title); layout.addWidget(body); grid.addWidget(card, index // 2, index % 2)
        panel = self.section("Algorithm map"); panel.layout().addLayout(grid); self.layout.addWidget(panel); self.layout.addStretch()
