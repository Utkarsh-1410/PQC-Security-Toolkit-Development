from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit

from pqc_toolkit.crypto.base import BackendUnavailable
from pqc_toolkit.crypto.file_vault import decrypt_file, encrypt_file
from pqc_toolkit.utils import format_bytes
from .page_base import Page


class FileSecurityPage(Page):
    notify = Signal(str, bool)

    def __init__(self, parent=None) -> None:
        super().__init__("Secure File Vault", "Hybrid Post-Quantum Encryption\nML-KEM establishes a shared secret; AES-256-GCM encrypts the file contents.", parent)
        select = self.section("File selection")
        self.path = QLineEdit(); self.path.setReadOnly(True); browse = self.button("Browse file"); browse.clicked.connect(self.browse)
        select.layout().addLayout(self.row(self.path, browse)); self.file_info = QLabel("No file selected"); self.file_info.setStyleSheet("color: #94a3b8;"); select.layout().addWidget(self.file_info); self.layout.addWidget(select)
        action = self.section("Encryption and decryption")
        self.encrypt_button = self.button("Encrypt file", True); self.encrypt_button.clicked.connect(self.encrypt); self.encrypt_button.setEnabled(False); action.layout().addWidget(QLabel("ML-KEM-768 + AES-256-GCM")); action.layout().addWidget(self.encrypt_button)
        self.decrypt_button = self.button("Decrypt selected .pqc"); self.decrypt_button.clicked.connect(self.decrypt); self.decrypt_button.setEnabled(False); action.layout().addWidget(self.decrypt_button); self.result = QLabel(); action.layout().addWidget(self.result); self.layout.addWidget(action)
        note = QLabel("Private key material remains in memory only for this session. It is never logged, written to the package, or saved to benchmark history."); note.setWordWrap(True); note.setStyleSheet("color: #f59e0b; background: #1e1b12; border: 1px solid #6b4d16; border-radius: 8px; padding: 12px;"); self.layout.addWidget(note); self.selected = None; self._private_key = None; self.layout.addStretch()

    def browse(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Select file")
        if filename:
            self.selected = Path(filename); self.path.setText(str(self.selected)); self.file_info.setText(f"{self.selected.name}  •  {format_bytes(self.selected.stat().st_size)}"); self.encrypt_button.setEnabled(self.selected.suffix != ".pqc"); self.decrypt_button.setEnabled(self.selected.suffix == ".pqc" and self._private_key is not None)

    def encrypt(self) -> None:
        try:
            destination = self.selected.with_suffix(self.selected.suffix + ".pqc"); metadata = encrypt_file(self.selected, destination); self._private_key = metadata.pop("_private_key"); self.selected = destination; self.path.setText(str(destination)); self.result.setText(f"✓ FILE ENCRYPTED\n{destination}\n{metadata['cipher']}"); self.decrypt_button.setEnabled(True); self.notify.emit("File encrypted successfully", True)
        except (BackendUnavailable, Exception) as exc: self.notify.emit(str(exc), False)

    def decrypt(self) -> None:
        try:
            if not self._private_key or self.selected.suffix != ".pqc":
                self.notify.emit("Select a package encrypted in this session first", False)
                return
            destination = self.selected.with_suffix(""); metadata = decrypt_file(self.selected, destination, self._private_key); self.result.setText(f"✓ DECRYPTION SUCCESSFUL\n{destination}\n{metadata['filename']}"); self.notify.emit("File decrypted successfully", True)
        except (BackendUnavailable, Exception) as exc: self.notify.emit(f"Decryption failed: {exc}", False)
