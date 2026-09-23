from __future__ import annotations

import statistics
import time
from dataclasses import asdict, dataclass
from typing import Callable

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class BenchmarkResult:
    algorithm: str
    operation: str
    iterations: int
    average_ms: float
    minimum_ms: float
    maximum_ms: float
    stdev_ms: float
    memory_mb: float | None
    sizes: dict[str, int]


class BenchmarkEngine:
    def run(self, algorithm: str, operation: str, callback: Callable[[], object], sizes: dict[str, int], iterations: int, warmup: int, progress: Callable[[int], None] | None = None) -> BenchmarkResult:
        for _ in range(warmup):
            callback()
        before = psutil.Process().memory_info().rss / 1024 / 1024 if psutil else None
        samples: list[float] = []
        for index in range(iterations):
            started = time.perf_counter()
            callback()
            samples.append((time.perf_counter() - started) * 1000)
            if progress:
                progress(index + 1)
        after = psutil.Process().memory_info().rss / 1024 / 1024 if psutil else None
        return BenchmarkResult(algorithm, operation, iterations, statistics.fmean(samples), min(samples), max(samples), statistics.stdev(samples) if len(samples) > 1 else 0.0, (after - before) if before is not None and after is not None else None, sizes)


def result_dict(result: BenchmarkResult) -> dict[str, object]:
    return asdict(result)
