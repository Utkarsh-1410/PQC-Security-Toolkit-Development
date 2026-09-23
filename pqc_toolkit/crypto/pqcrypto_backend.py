from __future__ import annotations

import importlib
import time
from types import ModuleType

from .base import BackendUnavailable, EncapsulationResult, KeyPair, SignatureResult


def _load(module_name: str) -> ModuleType:
    try:
        return importlib.import_module(module_name)
    except ImportError as exc:
        raise BackendUnavailable(
            "The optional pqcrypto package is unavailable. Install requirements.txt "
            "to enable standardized PQC operations."
        ) from exc


class PQCryptoKEM:
    def __init__(self, variant: str = "ML-KEM-768") -> None:
        self.variant = variant
        self.name = variant
        self.variants = ("ML-KEM-512", "ML-KEM-768", "ML-KEM-1024")
        module_variant = variant.lower().replace("-", "_")
        self._module = _load(f"pqcrypto.kem.{module_variant}")

    def generate_keypair(self) -> KeyPair:
        started = time.perf_counter()
        keygen = getattr(self._module, "keygen", None) or getattr(self._module, "generate_keypair")
        public_key, private_key = keygen()
        return KeyPair(public_key, private_key, (time.perf_counter() - started) * 1000)

    def encapsulate(self, public_key: bytes) -> EncapsulationResult:
        started = time.perf_counter()
        encaps = getattr(self._module, "encaps", None) or getattr(self._module, "encrypt")
        ciphertext, secret = encaps(public_key)
        return EncapsulationResult(ciphertext, secret, (time.perf_counter() - started) * 1000)

    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes:
        if hasattr(self._module, "decaps"):
            return self._module.decaps(private_key, ciphertext)
        return self._module.decrypt(ciphertext, private_key)

    def sizes(self) -> dict[str, int]:
        return {
            "public_key": getattr(self._module, "PUBLIC_KEY_SIZE", None) or getattr(self._module, "PUBLICKEYBYTES"),
            "private_key": getattr(self._module, "SECRET_KEY_SIZE", None) or getattr(self._module, "SECRETKEYBYTES"),
            "ciphertext": getattr(self._module, "CIPHERTEXT_SIZE", None) or getattr(self._module, "CIPHERTEXTBYTES"),
            "shared_secret": getattr(self._module, "SHARED_SECRET_SIZE", None) or getattr(self._module, "BYTES_IN_SHARED_SECRET"),
        }


class PQCryptoSignature:
    def __init__(self, variant: str = "ML-DSA-65") -> None:
        self.variant = variant
        self.name = variant
        self.variants = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
        module_variant = variant.lower().replace("-", "_")
        self._module = _load(f"pqcrypto.sign.{module_variant}")

    def generate_keypair(self) -> KeyPair:
        started = time.perf_counter()
        keygen = getattr(self._module, "keygen", None) or getattr(self._module, "generate_keypair")
        public_key, private_key = keygen()
        return KeyPair(public_key, private_key, (time.perf_counter() - started) * 1000)

    def sign(self, message: bytes, private_key: bytes) -> SignatureResult:
        started = time.perf_counter()
        try:
            signature = self._module.sign(private_key, message)
        except TypeError:
            signature = self._module.sign(message, private_key)
        return SignatureResult(signature, (time.perf_counter() - started) * 1000)

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        try:
            result = self._module.verify(public_key, message, signature)
            return True if result is None else bool(result)
        except (ValueError, TypeError):
            return False

    def sizes(self) -> dict[str, int]:
        return {
            "public_key": getattr(self._module, "PUBLIC_KEY_SIZE", None) or getattr(self._module, "PUBLICKEYBYTES"),
            "private_key": getattr(self._module, "SECRET_KEY_SIZE", None) or getattr(self._module, "SECRETKEYBYTES"),
            "signature": getattr(self._module, "SIGNATURE_SIZE", None) or getattr(self._module, "BYTES"),
        }


class PQCryptoSLHDSA(PQCryptoSignature):
    def __init__(self, variant: str = "SLH-DSA-SHA2-128S") -> None:
        self.variant = variant
        self.name = variant
        self.variants = (
            "SLH-DSA-SHA2-128S",
            "SLH-DSA-SHA2-128F",
            "SLH-DSA-SHA2-192S",
            "SLH-DSA-SHA2-192F",
            "SLH-DSA-SHA2-256S",
            "SLH-DSA-SHA2-256F",
        )
        candidates = [
            variant.lower().replace("-", "_"),
            variant.lower().replace("slh-dsa-", "slh_dsa_").replace("-", "_").replace("sha2_", "sha2_")
        ]
        for candidate in candidates:
            try:
                self._module = _load(f"pqcrypto.sign.{candidate}")
                return
            except BackendUnavailable:
                continue
        raise BackendUnavailable(f"No pqcrypto SLH-DSA provider found for {variant}.")
