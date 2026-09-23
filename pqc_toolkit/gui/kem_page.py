from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit, QComboBox, QPushButton

from pqc_toolkit.crypto.base import BackendUnavailable
from pqc_toolkit.crypto.pqcrypto_backend import PQCryptoKEM
from pqc_toolkit.utils import decode_bytes, encode_bytes, format_bytes
from .page_base import Page


class KEMPage(Page):
    notify = Signal(str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__("ML-KEM", "Key Encapsulation Mechanism\nGenerate post-quantum key pairs and demonstrate encapsulation and decapsulation.", parent)
        controls = self.section("Algorithm")
        row = QHBoxLayout(); self.algorithm = QComboBox(); self.algorithm.addItems(["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"])
        generate = self.button("Generate key pair", True); generate.clicked.connect(self.generate)
        row.addWidget(QLabel("Algorithm")); row.addWidget(self.algorithm); row.addStretch(); row.addWidget(generate); controls.layout().addLayout(row); self.layout.addWidget(controls)
        self.stats = QLabel("No key pair loaded")
        self.stats.setStyleSheet("color: #94a3b8; font-size: 14px;")
        self.layout.addWidget(self.stats)
        keys = self.section("Key material")
        form = QFormLayout(); self.public_view = QPlainTextEdit(); self.public_view.setReadOnly(True); self.public_view.setMaximumHeight(100)
        self.private_view = QPlainTextEdit(); self.private_view.setReadOnly(True); self.private_view.setMaximumHeight(100); self.private_view.setPlainText("Private key hidden until generated")
        form.addRow("Public key", self.public_view); form.addRow("Private key", self.private_view); keys.layout().addLayout(form); self.layout.addWidget(keys)
        encapsulation = self.section("Encapsulation")
        self.encapsulate_button = self.button("Encapsulate", True); self.encapsulate_button.clicked.connect(self.encapsulate); self.encapsulate_button.setEnabled(False)
        self.ciphertext = QLineEdit(); self.ciphertext.setReadOnly(True); self.secret = QLineEdit(); self.secret.setReadOnly(True); self.secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_secret = QPushButton("Show secret"); self.show_secret.clicked.connect(self.toggle_secret)
        encapsulation.layout().addLayout(self.row(self.encapsulate_button)); encapsulation.layout().addWidget(QLabel("Ciphertext")); encapsulation.layout().addWidget(self.ciphertext); encapsulation.layout().addWidget(QLabel("Shared secret (hidden)")); encapsulation.layout().addWidget(self.secret); encapsulation.layout().addWidget(self.show_secret); self.layout.addWidget(encapsulation)
        decapsulation = self.section("Decapsulation")
        self.decrypt_input = QPlainTextEdit(); self.decrypt_input.setPlaceholderText("Paste ciphertext here"); self.decrypt_button = self.button("Decapsulate", True); self.decrypt_button.clicked.connect(self.decapsulate); self.decrypt_button.setEnabled(False)
        self.recovered_secret = QLineEdit(); self.recovered_secret.setReadOnly(True); self.recovered_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.show_recovered = QPushButton("Show recovered secret"); self.show_recovered.clicked.connect(lambda: self.toggle_echo(self.recovered_secret))
        self.decap_result = QLabel("No decapsulation attempted")
        self.decap_result.setStyleSheet("color: #94a3b8; font-weight: 600;")
        decapsulation.layout().addWidget(self.decrypt_input); decapsulation.layout().addWidget(self.decrypt_button); decapsulation.layout().addWidget(QLabel("Recovered secret")); decapsulation.layout().addWidget(self.recovered_secret); decapsulation.layout().addWidget(self.show_recovered); decapsulation.layout().addWidget(self.decap_result); self.layout.addWidget(decapsulation)
        self._backend = None; self._keys = None; self._encapsulation = None
        self.layout.addStretch()

    def generate(self) -> None:
        try:
            self._backend = PQCryptoKEM(self.algorithm.currentText()); self._keys = self._backend.generate_keypair(); sizes = self._backend.sizes()
            self.public_view.setPlainText(encode_bytes(self._keys.public_key)); self.private_view.setPlainText("•" * 52); self.stats.setText(f"Public key {format_bytes(sizes['public_key'])}  •  Private key {format_bytes(sizes['private_key'])}  •  Generated in {self._keys.generated_ms:.2f} ms")
            self.encapsulate_button.setEnabled(True); self.decrypt_button.setEnabled(True); self.notify.emit("Key pair generated successfully", True)
            self.ciphertext.clear(); self.secret.clear(); self.recovered_secret.clear(); self.decap_result.setText("No decapsulation attempted")
        except (BackendUnavailable, Exception) as exc:
            self.notify.emit(str(exc), False)

    def encapsulate(self) -> None:
        try:
            self._encapsulation = self._backend.encapsulate(self._keys.public_key); self.ciphertext.setText(encode_bytes(self._encapsulation.ciphertext)); self.secret.setText(encode_bytes(self._encapsulation.shared_secret)); self.decrypt_input.setPlainText(encode_bytes(self._encapsulation.ciphertext)); self.notify.emit("Shared secret encapsulated", True)
        except Exception as exc:
            self.notify.emit(f"Encapsulation failed: {exc}", False)

    def decapsulate(self) -> None:
        if not self._keys or not self._backend: self.notify.emit("Generate a key pair before decapsulating", False); return
        try:
            ciphertext = decode_bytes(self.decrypt_input.toPlainText().strip() or self.ciphertext.text())
            recovered = self._backend.decapsulate(self._keys.private_key, ciphertext)
            self.recovered_secret.setText(encode_bytes(recovered))
            original = (self.secret.text() or encode_bytes(self._encapsulation.shared_secret) if self._encapsulation else "")
            match = original and encode_bytes(recovered) == original
            if match:
                self.decap_result.setText("✓ DECAPSULATION SUCCESSFUL\nRecovered secret matches original secret.")
                self.decap_result.setStyleSheet("color: #22c55e; font-weight: 700;")
                self.notify.emit("Shared secret recovered successfully", True)
            else:
                self.decap_result.setText("✕ DECAPSULATION FAILED\nRecovered secret does not match the original value.")
                self.decap_result.setStyleSheet("color: #ef4444; font-weight: 700;")
                self.notify.emit("Shared secret mismatch", False)
        except Exception as exc:
            self.decap_result.setText(f"✕ DECAPSULATION FAILED\n{exc}")
            self.decap_result.setStyleSheet("color: #ef4444; font-weight: 700;")
            self.notify.emit(f"Decapsulation failed: {exc}", False)

    def toggle_secret(self) -> None:
        self.toggle_echo(self.secret)

    @staticmethod
    def toggle_echo(field: QLineEdit) -> None:
        field.setEchoMode(QLineEdit.EchoMode.Normal if field.echoMode() == QLineEdit.EchoMode.Password else QLineEdit.EchoMode.Password)
