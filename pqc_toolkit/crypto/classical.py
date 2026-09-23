from __future__ import annotations

import time

from .base import BackendUnavailable, KeyPair, SignatureResult


class ClassicalRSA:
    """Optional classical reference backend for neutral comparisons."""

    def __init__(self, bits: int = 2048) -> None:
        try:
            from cryptography.hazmat.primitives.asymmetric import padding, rsa
            from cryptography.hazmat.primitives import hashes, serialization
        except ImportError as exc:
            raise BackendUnavailable("Install cryptography to enable RSA comparisons.") from exc
        self._rsa = rsa
        self._padding = padding
        self._hashes = hashes
        self._serialization = serialization
        self.bits = bits
        self.name = f"RSA-{bits}"

    def generate_keypair(self) -> KeyPair:
        started = time.perf_counter()
        private = self._rsa.generate_private_key(public_exponent=65537, key_size=self.bits)
        public = private.public_key()
        public_bytes = public.public_bytes(self._serialization.Encoding.DER, self._serialization.PublicFormat.SubjectPublicKeyInfo)
        private_bytes = private.private_bytes(self._serialization.Encoding.DER, self._serialization.PrivateFormat.PKCS8, self._serialization.NoEncryption())
        return KeyPair(public_bytes, private_bytes, (time.perf_counter() - started) * 1000)

    def sign(self, message: bytes, private_key: bytes) -> SignatureResult:
        started = time.perf_counter()
        private = self._serialization.load_der_private_key(private_key, password=None)
        signature = private.sign(message, self._padding.PKCS1v15(), self._hashes.SHA256())
        return SignatureResult(signature, (time.perf_counter() - started) * 1000)
