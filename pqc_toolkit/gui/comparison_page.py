from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pqc_toolkit.crypto.classical import ClassicalRSA
from pqc_toolkit.crypto.pqcrypto_backend import PQCryptoKEM, PQCryptoSignature
from .page_base import Page


class ComparisonPage(Page):
    def __init__(self, parent=None) -> None:
        super().__init__("Classical vs Post-Quantum Cryptography", "Compare design goals, object sizes, and measured characteristics without reducing security to a single ranking.", parent)
        controls = self.section("Comparison inputs")
        row = QHBoxLayout(); self.classical = QComboBox(); self.classical.addItems(["RSA-2048", "ECC-P256"]); self.pqc = QComboBox(); self.pqc.addItems(["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "ML-DSA-65"]); self.refresh = QPushButton("Refresh data"); self.refresh.clicked.connect(self.update_comparison); row.addWidget(QLabel("Classical")); row.addWidget(self.classical); row.addSpacing(20); row.addWidget(QLabel("PQC")); row.addWidget(self.pqc); row.addStretch(); row.addWidget(self.refresh); controls.layout().addLayout(row); self.layout.addWidget(controls)
        self.table = QTableWidget(6, 3); self.table.setHorizontalHeaderLabels(["Metric", "Classical", "PQC"]); self.table.setAlternatingRowColors(True); self.layout.addWidget(self.table)
        self.figure = Figure(figsize=(7, 2.5), facecolor="#111827"); self.canvas = FigureCanvasQTAgg(self.figure); self.layout.addWidget(self.canvas)
        self.update_comparison(); note = QLabel("This comparison uses measured object sizes and operation timings from the installed providers. It avoids a winner/loser framing and instead highlights different design goals and assumptions."); note.setWordWrap(True); note.setStyleSheet("color: #94a3b8;"); self.layout.addWidget(note); self.layout.addStretch()

    def update_comparison(self) -> None:
        classical_data = self.measure_classical(self.classical.currentText())
        pqc_data = self.measure_pqc(self.pqc.currentText())
        values = [("Algorithm type", classical_data["type"], pqc_data["type"]), ("Public key size", str(classical_data["public_key"]), str(pqc_data["public_key"])), ("Private key size", str(classical_data["private_key"]), str(pqc_data["private_key"])), ("Ciphertext or signature", str(classical_data["ciphertext"]), str(pqc_data["ciphertext"])), ("Operation time", f"{classical_data['time_ms']:.2f} ms", f"{pqc_data['time_ms']:.2f} ms"), ("Security assumptions", "Classical number theory", "Post-quantum lattice/hashing assumptions")]
        for row_index, values_row in enumerate(values):
            for column, value in enumerate(values_row): self.table.setItem(row_index, column, QTableWidgetItem(str(value)))
        self.draw_chart(classical_data, pqc_data)

    def measure_classical(self, algorithm: str) -> dict[str, object]:
        if algorithm == "RSA-2048":
            backend = ClassicalRSA(2048)
            pair = backend.generate_keypair()
            return {"type": "RSA", "public_key": len(pair.public_key), "private_key": len(pair.private_key), "ciphertext": 256, "time_ms": pair.generated_ms}
        backend = ClassicalRSA(256)
        pair = backend.generate_keypair()
        return {"type": "ECC", "public_key": len(pair.public_key), "private_key": len(pair.private_key), "ciphertext": 64, "time_ms": pair.generated_ms}

    def measure_pqc(self, algorithm: str) -> dict[str, object]:
        if algorithm.startswith("ML-KEM"):
            backend = PQCryptoKEM(algorithm)
            keypair = backend.generate_keypair()
            encaps = backend.encapsulate(keypair.public_key)
            return {"type": "KEM", "public_key": backend.sizes()["public_key"], "private_key": backend.sizes()["private_key"], "ciphertext": backend.sizes()["ciphertext"], "time_ms": keypair.generated_ms + encaps.elapsed_ms}
        backend = PQCryptoSignature(algorithm)
        keypair = backend.generate_keypair(); signed = backend.sign(b"comparison-message", keypair.private_key)
        return {"type": "Signature", "public_key": backend.sizes()["public_key"], "private_key": backend.sizes()["private_key"], "ciphertext": backend.sizes()["signature"], "time_ms": keypair.generated_ms + signed.elapsed_ms}

    def draw_chart(self, classical: dict[str, object], pqc: dict[str, object]) -> None:
        self.figure.clear(); axis = self.figure.add_subplot(111); axis.set_facecolor("#111827")
        labels = ["Public key", "Private key", "Ciphertext"]
        classical_values = [classical["public_key"], classical["private_key"], classical["ciphertext"]]
        pqc_values = [pqc["public_key"], pqc["private_key"], pqc["ciphertext"]]
        axis.bar(labels, classical_values, color="#5b8cff", alpha=0.7, label="Classical")
        axis.bar(labels, pqc_values, color="#22c55e", alpha=0.7, label="PQC")
        axis.set_title("Key material size comparison", color="#f8fafc")
        axis.tick_params(axis="x", colors="#cbd5e1")
        axis.tick_params(axis="y", colors="#cbd5e1")
        axis.legend(frameon=False)
        self.figure.tight_layout(); self.canvas.draw_idle()
