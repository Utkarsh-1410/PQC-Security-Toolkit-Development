from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pqc_toolkit.utils import load_json, save_json


class BenchmarkStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def list(self) -> list[dict[str, object]]:
        return load_json(self.path, [])

    def append(self, result: dict[str, object]) -> None:
        entries = self.list()
        entries.insert(0, {"timestamp": datetime.now(timezone.utc).isoformat(), **result})
        save_json(self.path, entries[:100])

    def clear(self) -> None:
        save_json(self.path, [])
