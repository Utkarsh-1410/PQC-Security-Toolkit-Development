from __future__ import annotations

import csv
import json
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QCheckBox, QComboBox, QFileDialog, QGridLayout, QHBoxLayout, QLabel, QProgressBar, QSpinBox, QTableWidget, QTableWidgetItem

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pqc_toolkit.benchmark.engine import BenchmarkEngine, result_dict
from pqc_toolkit.benchmark.store import BenchmarkStore
from pqc_toolkit.crypto.base import BackendUnavailable
from pqc_toolkit.crypto.pqcrypto_backend import PQCryptoKEM, PQCryptoSignature
from .page_base import Page


class BenchmarkWorker(QObject):
    progress = Signal(int, int)
    completed = Signal(list)
    failed = Signal(str)

    def __init__(self, operation: str, algorithms: list[str], iterations: int, warmup: int) -> None:
        super().__init__(); self.operation = operation; self.algorithms = algorithms; self.iterations = iterations; self.warmup = warmup

    @staticmethod
    def build_backend(algorithm: str):
        if algorithm.startswith("ML-KEM"):
            return PQCryptoKEM(algorithm)
        if algorithm.startswith("ML-DSA") or algorithm.startswith("SLH"):
            return PQCryptoSignature(algorithm)
        raise BackendUnavailable(f"Unsupported benchmark algorithm: {algorithm}")

    @Slot()
    def run(self) -> None:
        try:
            results: list[dict] = []
            for index, algorithm in enumerate(self.algorithms, start=1):
                backend = self.build_backend(algorithm)
                engine = BenchmarkEngine()
                if self.operation == "Key Generation":
                    callback = backend.generate_keypair
                    result = engine.run(algorithm, "key generation", callback, backend.sizes(), self.iterations, self.warmup)
                elif self.operation == "Encapsulation":
                    keypair = backend.generate_keypair(); callback = lambda: backend.encapsulate(keypair.public_key)
                    result = engine.run(algorithm, "encapsulation", callback, backend.sizes(), self.iterations, self.warmup)
                elif self.operation == "Signature":
                    keypair = backend.generate_keypair(); callback = lambda: backend.sign(b"benchmark-signature-message", keypair.private_key)
                    result = engine.run(algorithm, "signature", callback, backend.sizes(), self.iterations, self.warmup)
                else:
                    raise BackendUnavailable("Unsupported benchmark operation.")
                results.append(result_dict(result))
                self.progress.emit(index, len(self.algorithms))
            self.completed.emit(results)
        except Exception as exc: self.failed.emit(str(exc))


class BenchmarkPage(Page):
    notify = Signal(str, bool)

    def __init__(self, store: BenchmarkStore, parent=None) -> None:
        super().__init__("Performance Benchmark", "Measure execution time, memory usage, and cryptographic object sizes across actual provider operations.", parent)
        self.store = store; self.thread = None; self.worker = None
        controls = self.section("Experiment controls")
        row = QHBoxLayout(); self.operation = QComboBox(); self.operation.addItems(["Key Generation", "Encapsulation", "Signature"]); self.iterations = QSpinBox(); self.iterations.setRange(1, 2000); self.iterations.setValue(100); self.warmup = QSpinBox(); self.warmup.setRange(0, 1000); self.warmup.setValue(10); self.run_button = self.button("Run benchmark", True); self.run_button.clicked.connect(self.run_benchmark); row.addWidget(QLabel("Operation")); row.addWidget(self.operation); row.addWidget(QLabel("Iterations")); row.addWidget(self.iterations); row.addWidget(QLabel("Warm-up")); row.addWidget(self.warmup); row.addWidget(self.run_button); controls.layout().addLayout(row)
        self.layout.addWidget(controls)
        self.algorithm_checks = {}
        algorithm_grid = QGridLayout(); algos = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87", "SLH-DSA-SHA2-128S"]
        for index, algorithm in enumerate(algos):
            checkbox = QCheckBox(algorithm)
            checkbox.setChecked(index < 3)
            self.algorithm_checks[algorithm] = checkbox
            algorithm_grid.addWidget(checkbox, index // 3, index % 3)
        select = self.section("Algorithms")
        select.layout().addLayout(algorithm_grid)
        self.layout.addWidget(select)
        self.progress = QProgressBar(); self.progress.setRange(0, 100); self.progress.hide(); self.status = QLabel("Ready"); self.status.setStyleSheet("color: #94a3b8;"); self.layout.addWidget(self.progress); self.layout.addWidget(self.status)
        self.table = QTableWidget(0, 7); self.table.setHorizontalHeaderLabels(["Algorithm", "Avg", "Min", "Max", "Std dev", "Memory", "Iterations"]); self.layout.addWidget(self.table)
        self.figure = Figure(figsize=(7, 2.4), facecolor="#111827"); self.canvas = FigureCanvasQTAgg(self.figure)
        self.layout.addWidget(self.canvas)
        self.export_csv_button = self.button("Export CSV"); self.export_csv_button.clicked.connect(self.export_csv)
        self.export_json_button = self.button("Export JSON"); self.export_json_button.clicked.connect(self.export_json)
        self.export_png_button = self.button("Export PNG"); self.export_png_button.clicked.connect(self.export_png)
        export_row = QHBoxLayout(); export_row.addWidget(self.export_csv_button); export_row.addWidget(self.export_json_button); export_row.addWidget(self.export_png_button); self.layout.addLayout(export_row)
        self.layout.addStretch(); self.load_history()

    def selected_algorithms(self) -> list[str]:
        return [name for name, checkbox in self.algorithm_checks.items() if checkbox.isChecked()]

    def run_benchmark(self) -> None:
        algorithms = self.selected_algorithms()
        if not algorithms:
            self.notify.emit("Select at least one algorithm to benchmark.", False); return
        self.run_button.setEnabled(False); self.progress.show(); self.progress.setValue(0); self.thread = QThread(); self.worker = BenchmarkWorker(self.operation.currentText(), algorithms, self.iterations.value(), self.warmup.value()); self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run); self.worker.progress.connect(lambda current, total: (self.progress.setValue(int((current / total) * 100) if total else 0), self.status.setText(f"Running {self.operation.currentText()}  •  algorithm {current} / {total}"))); self.worker.completed.connect(self.finished); self.worker.failed.connect(self.failed); self.worker.completed.connect(self.thread.quit); self.worker.failed.connect(self.thread.quit); self.thread.finished.connect(lambda: self.run_button.setEnabled(True)); self.thread.start()

    def finished(self, results: list[dict]) -> None:
        for row in results:
            self.store.append(row)
        self.load_history(); self.notify.emit("Benchmark completed", True); self.status.setText("Benchmark complete")

    def failed(self, message: str) -> None:
        self.notify.emit(message, False); self.status.setText("Benchmark failed")

    def load_history(self) -> None:
        entries = self.store.list(); self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            values = [entry.get("algorithm", ""), f"{entry.get('average_ms', 0):.3f} ms", f"{entry.get('minimum_ms', 0):.3f} ms", f"{entry.get('maximum_ms', 0):.3f} ms", f"{entry.get('stdev_ms', 0):.3f} ms", f"{entry.get('memory_mb', 0) or 0:.2f} MB", str(entry.get("iterations", ""))]
            for column, value in enumerate(values): self.table.setItem(row, column, QTableWidgetItem(value))
        axis = self.figure.clear() or self.figure.add_subplot(111)
        axis.set_facecolor("#111827")
        if entries:
            labels = [str(entry.get("algorithm", "")) for entry in entries[:12]]
            averages = [float(entry.get("average_ms", 0)) for entry in entries[:12]]
            axis.bar(labels, averages, color="#5b8cff")
            axis.set_ylabel("ms", color="#94a3b8")
            axis.tick_params(axis="x", colors="#cbd5e1", rotation=20)
            axis.tick_params(axis="y", colors="#cbd5e1")
            axis.set_title("Measured average operation time", color="#f8fafc")
        else:
            axis.text(0.5, 0.5, "Run a benchmark to populate measured results", color="#94a3b8", ha="center", va="center")
            axis.set_axis_off()
        self.figure.tight_layout(); self.canvas.draw_idle()

    def export_csv(self) -> None:
        if not self.store.list(): self.notify.emit("No benchmark data available to export.", False); return
        path, _ = QFileDialog.getSaveFileName(self, "Export benchmark CSV", "benchmark_results.csv", "CSV Files (*.csv)")
        if not path: return
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["algorithm", "operation", "iterations", "average_ms", "minimum_ms", "maximum_ms", "stdev_ms", "memory_mb"])
            for entry in self.store.list():
                writer.writerow([entry.get("algorithm", ""), entry.get("operation", ""), entry.get("iterations", ""), entry.get("average_ms", 0), entry.get("minimum_ms", 0), entry.get("maximum_ms", 0), entry.get("stdev_ms", 0), entry.get("memory_mb", 0)])
        self.notify.emit("CSV export complete", True)

    def export_json(self) -> None:
        entries = self.store.list()
        if not entries: self.notify.emit("No benchmark data available to export.", False); return
        path, _ = QFileDialog.getSaveFileName(self, "Export benchmark JSON", "benchmark_results.json", "JSON Files (*.json)")
        if not path: return
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(entries, handle, indent=2)
        self.notify.emit("JSON export complete", True)

    def export_png(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Export benchmark PNG", "benchmark_results.png", "PNG Files (*.png)")
        if not path: return
        self.figure.savefig(path, dpi=200, facecolor="#111827")
        self.notify.emit("PNG export complete", True)
