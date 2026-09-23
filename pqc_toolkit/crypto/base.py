from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class BackendUnavailable(RuntimeError):
    """Raised when the configured cryptographic provider is unavailable."""


@dataclass(frozen=True)
class KeyPair:
    public_key: bytes
    private_key: bytes
    generated_ms: float


@dataclass(frozen=True)
class EncapsulationResult:
    ciphertext: bytes
    shared_secret: bytes
    elapsed_ms: float


@dataclass(frozen=True)
class SignatureResult:
    signature: bytes
    elapsed_ms: float


class KEMBackend(Protocol):
    name: str
    variants: tuple[str, ...]

    def generate_keypair(self) -> KeyPair: ...
    def encapsulate(self, public_key: bytes) -> EncapsulationResult: ...
    def decapsulate(self, private_key: bytes, ciphertext: bytes) -> bytes: ...
    def sizes(self) -> dict[str, int]: ...


class SignatureBackend(Protocol):
    name: str
    variants: tuple[str, ...]

    def generate_keypair(self) -> KeyPair: ...
    def sign(self, message: bytes, private_key: bytes) -> SignatureResult: ...
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool: ...
    def sizes(self) -> dict[str, int]: ...
