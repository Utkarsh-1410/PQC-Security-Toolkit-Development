from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QPlainTextEdit

from pqc_toolkit.crypto.base import BackendUnavailable
from pqc_toolkit.crypto.pqcrypto_backend import PQCryptoSignature
from pqc_toolkit.utils import encode_bytes, format_bytes
from .page_base import Page


class SignaturesPage(Page):
    notify = Signal(str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__("Digital Signatures", "Create and verify post-quantum digital signatures with real provider-backed operations.", parent)
        controls = self.section("Signing provider")
        row = QHBoxLayout(); self.algorithm = QComboBox(); self.algorithm.addItems(["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]); generate = self.button("Generate signing keys", True); generate.clicked.connect(self.generate)
        row.addWidget(QLabel("Algorithm")); row.addWidget(self.algorithm); row.addStretch(); row.addWidget(generate); controls.layout().addLayout(row); self.layout.addWidget(controls)
        self.key_status = QLabel("No signing key pair loaded"); self.key_status.setStyleSheet("color: #94a3b8;"); self.layout.addWidget(self.key_status)
        message = self.section("Message signing")
        self.message = QPlainTextEdit(); self.message.setPlaceholderText("Enter the message you want to sign..."); self.message.setMinimumHeight(100); sign = self.button("Sign message", True); sign.clicked.connect(self.sign); sign.setEnabled(False); self.sign_button = sign
        self.signature = QLineEdit(); self.signature.setReadOnly(True)
        message.layout().addWidget(self.message); message.layout().addWidget(sign); message.layout().addWidget(QLabel("Signature")); message.layout().addWidget(self.signature); self.layout.addWidget(message)
        verify = self.section("Verify signature")
        self.verify_message = QPlainTextEdit(); self.verify_message.setPlaceholderText("Enter original message..."); self.verify_message.setMaximumHeight(80); self.verify_signature = QLineEdit(); self.verify_signature.setPlaceholderText("Paste base64 signature..."); verify_button = self.button("Verify", True); verify_button.clicked.connect(self.verify)
        verify.layout().addWidget(self.verify_message); verify.layout().addWidget(self.verify_signature); verify.layout().addWidget(verify_button); self.verify_result = QLabel(); verify.layout().addWidget(self.verify_result); self.layout.addWidget(verify)
        self._backend = None; self._keys = None; self.layout.addStretch()

    def generate(self) -> None:
        try:
            self._backend = PQCryptoSignature(self.algorithm.currentText()); self._keys = self._backend.generate_keypair(); sizes = self._backend.sizes(); self.key_status.setText(f"Keys ready  •  Public {format_bytes(sizes['public_key'])}  •  Private {format_bytes(sizes['private_key'])}  •  {self._keys.generated_ms:.2f} ms"); self.sign_button.setEnabled(True); self.notify.emit("Signing keys generated successfully", True)
        except (BackendUnavailable, Exception) as exc:
            self.notify.emit(str(exc), False)

    def sign(self) -> None:
        if not self._keys or not self.message.toPlainText(): self.notify.emit("Please provide a message and generate keys first", False); return
        try:
            result = self._backend.sign(self.message.toPlainText().encode(), self._keys.private_key); encoded = encode_bytes(result.signature); self.signature.setText(encoded); self.verify_message.setPlainText(self.message.toPlainText()); self.verify_signature.setText(encoded); self.notify.emit(f"Message signed in {result.elapsed_ms:.2f} ms", True)
        except Exception as exc: self.notify.emit(f"Signing failed: {exc}", False)

    def verify(self) -> None:
        if not self._keys: self.notify.emit("Generate signing keys first", False); return
        try:
            from pqc_toolkit.utils import decode_bytes
            valid = self._backend.verify(self.verify_message.toPlainText().encode(), decode_bytes(self.verify_signature.text()), self._keys.public_key); self.verify_result.setText("✓ SIGNATURE VALID" if valid else "✕ SIGNATURE INVALID"); self.verify_result.setStyleSheet(f"color: {'#22c55e' if valid else '#ef4444'}; font-weight: 700;"); self.notify.emit("Signature verified" if valid else "Verification failed", valid)
        except Exception as exc: self.notify.emit(f"Verification failed: {exc}", False)
