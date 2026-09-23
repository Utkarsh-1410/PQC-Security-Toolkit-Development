from __future__ import annotations

import json
import os
import struct
from pathlib import Path

from .base import BackendUnavailable
from .pqcrypto_backend import PQCryptoKEM

MAGIC = b"PQC1"


def encrypt_file(source: Path, destination: Path, algorithm: str = "ML-KEM-768") -> dict[str, object]:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives import hashes
    except ImportError as exc:
        raise BackendUnavailable("Install cryptography to enable hybrid file encryption.") from exc
    backend = PQCryptoKEM(algorithm)
    keypair = backend.generate_keypair()
    encapsulated = backend.encapsulate(keypair.public_key)
    aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pqc-toolkit-file").derive(encapsulated.shared_secret)
    nonce = os.urandom(12)
    ciphertext = AESGCM(aes_key).encrypt(nonce, source.read_bytes(), None)
    metadata = {"algorithm": algorithm, "cipher": "AES-256-GCM", "filename": source.name, "nonce": nonce.hex(), "encapsulation": encapsulated.ciphertext.hex()}
    encoded = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
    destination.write_bytes(MAGIC + struct.pack(">I", len(encoded)) + encoded + ciphertext)
    return metadata | {"output": str(destination), "bytes": destination.stat().st_size, "_private_key": keypair.private_key}


def decrypt_file(source: Path, destination: Path, private_key: bytes) -> dict[str, object]:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives import hashes
    except ImportError as exc:
        raise BackendUnavailable("Install cryptography to enable hybrid file decryption.") from exc
    payload = source.read_bytes()
    if payload[:4] != MAGIC:
        raise ValueError("Not a PQC Security Toolkit encrypted file.")
    header_size = struct.unpack(">I", payload[4:8])[0]
    metadata = json.loads(payload[8:8 + header_size])
    backend = PQCryptoKEM(metadata["algorithm"])
    shared_secret = backend.decapsulate(private_key, bytes.fromhex(metadata["encapsulation"]))
    aes_key = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pqc-toolkit-file").derive(shared_secret)
    plaintext = AESGCM(aes_key).decrypt(bytes.fromhex(metadata["nonce"]), payload[8 + header_size:], None)
    destination.write_bytes(plaintext)
    return metadata | {"output": str(destination), "bytes": destination.stat().st_size}
