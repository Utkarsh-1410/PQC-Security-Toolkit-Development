# PQC Security Toolkit

PQC Security Toolkit is a modular PySide6 desktop application for educational experimentation with standardized post-quantum cryptography.

## Features

- Provider-backed ML-KEM key generation, encapsulation, and decapsulation primitives.
- Provider-backed ML-DSA signing and verification.
- Hybrid ML-KEM plus AES-256-GCM file encryption.
- Threaded, measured benchmarks with CPU/memory observations and JSON history.
- Neutral classical versus post-quantum comparison and an educational overview.
- Sensitive values hidden by default and no private keys or secrets written to benchmark history.

## Architecture

`crypto/` contains backend contracts and adapters. `benchmark/` contains measurement and persistence services. `gui/` contains pages and widgets. The GUI never invents cryptographic values; unavailable providers are surfaced as an explicit error.

## Installation

Python 3.11+ is required. From this directory:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The `pqcrypto` package is the optional provider for ML-KEM and ML-DSA. `cryptography` provides AES-GCM and classical reference support. Confirm provider availability before relying on an operation:

```powershell
python -c "import pqcrypto, cryptography, PySide6"
```

## Running

From the repository root:

```powershell
python -m pqc_toolkit.main
```

The GUI opens even when `pqcrypto` is unavailable, but provider-dependent operations remain disabled through clear error states.

## Using The Toolkit

Generate ML-KEM keys, encapsulate a secret, and inspect provider-derived object sizes from the ML-KEM page. Generate a signing pair, sign a message, and verify or tamper with it from Digital Signatures. Select a file to create a `.pqc` package using ML-KEM key establishment and AES-256-GCM. Run measurements from Benchmark; each result is calculated from actual calls and stored in `data/benchmark_results.json`.

## Exporting Results

Benchmark history is JSON and intentionally contains measurement metadata only. Cryptographic material is never persisted by the benchmark store. Exporting private keys or shared secrets is deliberately not implemented in this educational baseline until an explicit custody workflow is added.

## Project Structure

- `main.py`: application entry point.
- `gui/`: Qt shell, pages, styles, and reusable widgets.
- `crypto/`: interfaces and provider adapters.
- `benchmark/`: threaded benchmark services and JSON history.
- `data/`: non-sensitive benchmark records.

## Security Considerations And Limitations

This is an educational and experimental application, not an audited cryptographic product. Install packages from trusted sources, protect private keys, and do not use the file vault for production data. The file vault supports a same-session decrypt round trip; it intentionally does not persist private-key recovery material, so a package cannot be decrypted after the application session ends.

## Future Improvements

Add an encrypted key store and explicit private-key import/export workflow, provider capability discovery for SLH-DSA, Matplotlib export panels, CSV/PNG export, richer benchmark operation selection, and a formal test suite against provider test vectors.
