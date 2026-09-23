from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QFormLayout, QSpinBox

from .page_base import Page


class SettingsPage(Page):
    def __init__(self, parent=None) -> None:
        super().__init__("Settings", "Control appearance, benchmark defaults, and sensitive-value handling.", parent)
        appearance = self.section("Appearance"); appearance.layout().addWidget(self.button("Dark theme  •  active")); self.layout.addWidget(appearance)
        benchmark = self.section("Benchmark"); form = QFormLayout(); iterations = QSpinBox(); iterations.setValue(100); warmup = QSpinBox(); warmup.setValue(10); form.addRow("Default iterations", iterations); form.addRow("Warm-up iterations", warmup); benchmark.layout().addLayout(form); benchmark.layout().addWidget(QCheckBox("Automatically save results")); self.layout.addWidget(benchmark)
        security = self.section("Security"); security.layout().addWidget(QCheckBox("Hide sensitive values by default", checked=True)); security.layout().addWidget(QCheckBox("Confirm secret export", checked=True)); security.layout().addWidget(QCheckBox("Clear sensitive fields after operation", checked=True)); self.layout.addWidget(security); self.layout.addStretch()
