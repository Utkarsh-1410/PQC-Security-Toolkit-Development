from __future__ import annotations

from PySide6.QtWidgets import QLabel

from .page_base import Page


class AboutPage(Page):
    def __init__(self, parent=None) -> None:
        super().__init__("PQC Security Toolkit", "Post-Quantum Cryptography Experimentation & Benchmarking Platform", parent)
        body = self.section("About this application"); label = QLabel("Version 1.0.0\n\nBuilt with Python, PySide6, Matplotlib, psutil, and provider-backed cryptographic libraries.\n\nThis application is intended for educational, research, and experimental purposes. Do not use it as a replacement for a professionally audited production cryptographic system."); label.setWordWrap(True); body.layout().addWidget(label); self.layout.addWidget(body); self.layout.addStretch()
