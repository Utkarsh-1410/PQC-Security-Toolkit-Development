from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from .page_base import Page
from .widgets import Card, MetricCard


class DashboardPage(Page):
    navigate = Signal(str)

    def __init__(self, backend_available: bool, parent=None) -> None:
        super().__init__("Post-Quantum Security", "Experimentation Platform\nExplore standardized PQC algorithms, perform cryptographic operations, and analyze their performance.", parent)
        metrics = QGridLayout()
        metrics.setSpacing(12)
        metrics.addWidget(MetricCard("PQC algorithms", "3", "ML-KEM • ML-DSA • SLH-DSA"), 0, 0)
        metrics.addWidget(MetricCard("Operations", "9", "Available workflows"), 0, 1)
        metrics.addWidget(MetricCard("Benchmarks", "0", "Experiments stored"), 0, 2)
        metrics.addWidget(MetricCard("System status", "READY" if backend_available else "LIMITED", "Crypto engine"), 0, 3)
        self.layout.addLayout(metrics)
        quick = self.section("Quick actions")
        quick_grid = QGridLayout(); quick_grid.setSpacing(10)
        actions = [("Generate ML-KEM keys", "kem"), ("Sign a message", "signatures"), ("Verify signature", "signatures"), ("Encrypt a file", "files"), ("Run benchmark", "benchmark"), ("Compare algorithms", "comparison")]
        for index, (text, page) in enumerate(actions):
            button = self.button(text)
            button.clicked.connect(lambda checked=False, target=page: self.navigate.emit(target))
            quick_grid.addWidget(button, index // 3, index % 3)
        quick.layout().addLayout(quick_grid)
        self.layout.addWidget(quick)
        algorithms = self.section("Standardized algorithms")
        grid = QGridLayout(); grid.setSpacing(12)
        for index, (name, kind, description, page) in enumerate([
            ("ML-KEM", "KEY ENCAPSULATION", "Module-lattice key establishment with encapsulation and decapsulation.", "kem"),
            ("ML-DSA", "DIGITAL SIGNATURE", "Module-lattice digital signatures for message authentication.", "signatures"),
            ("SLH-DSA", "HASH-BASED SIGNATURE", "Stateless hash-based signatures, parameterized by the provider.", "signatures"),
        ]):
            card = Card(); card_layout = QGridLayout(card)
            title = QLabel(name); title.setStyleSheet("font-size: 20px; font-weight: 700;")
            kind_label = QLabel(kind); kind_label.setObjectName("eyebrow")
            body = QLabel(description); body.setWordWrap(True); body.setStyleSheet("color: #94a3b8;")
            open_button = self.button("Open module  >", True); open_button.clicked.connect(lambda checked=False, target=page: self.navigate.emit(target))
            card_layout.addWidget(kind_label, 0, 0, 1, 2); card_layout.addWidget(title, 1, 0, 1, 2); card_layout.addWidget(body, 2, 0, 1, 2); card_layout.addWidget(open_button, 3, 1)
            grid.addWidget(card, 0, index)
        algorithms.layout().addLayout(grid)
        self.layout.addWidget(algorithms)
        self.layout.addStretch()
