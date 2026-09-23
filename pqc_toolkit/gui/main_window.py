from __future__ import annotations

import importlib.util
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QScrollArea, QStackedWidget, QVBoxLayout, QWidget

from pqc_toolkit import __version__
from pqc_toolkit.benchmark.store import BenchmarkStore
from .about_page import AboutPage
from .benchmark_page import BenchmarkPage
from .comparison_page import ComparisonPage
from .dashboard import DashboardPage
from .education_page import EducationPage
from .file_security_page import FileSecurityPage
from .kem_page import KEMPage
from .settings_page import SettingsPage
from .signatures_page import SignaturesPage
from .styles import DARK_STYLE
from .widgets import NavButton, Toast


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PQC Security Toolkit")
        self.setMinimumSize(1200, 750)
        self.resize(1440, 900)
        self.setStyleSheet(DARK_STYLE)
        self.backend_available = bool(importlib.util.find_spec("pqcrypto"))
        self.pages: dict[str, QWidget] = {}
        self.nav_buttons: dict[str, NavButton] = {}
        root = QWidget(); root_layout = QVBoxLayout(root); root_layout.setContentsMargins(0, 0, 0, 0); root_layout.setSpacing(0)
        root_layout.addWidget(self._topbar())
        body = QHBoxLayout(); body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0); body.addWidget(self._sidebar())
        self.stack = QStackedWidget(); body.addWidget(self.stack, 1); root_layout.addLayout(body, 1); self.setCentralWidget(root)
        self.toast = Toast(self); self.toast.setGeometry(30, 75, 420, 44)
        self._register_pages(); self.show_page("dashboard")
        timer = QTimer(self); timer.timeout.connect(self.update_metrics); timer.start(3000); self.update_metrics()

    def _topbar(self) -> QFrame:
        bar = QFrame(); bar.setObjectName("topBar"); bar.setFixedHeight(62); layout = QHBoxLayout(bar); layout.setContentsMargins(24, 0, 24, 0)
        title = QLabel("PQC SECURITY TOOLKIT"); title.setStyleSheet("font-weight: 700; letter-spacing: 1px;"); layout.addWidget(title); self.module_title = QLabel("Dashboard"); self.module_title.setStyleSheet("color: #94a3b8; margin-left: 18px;"); layout.addWidget(self.module_title); layout.addStretch(); self.system_status = QLabel(); layout.addWidget(self.system_status); version = QLabel(f"v{__version__}"); version.setStyleSheet("color: #64748b; margin-left: 18px;"); layout.addWidget(version); return bar

    def _sidebar(self) -> QFrame:
        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar.setFixedWidth(245); layout = QVBoxLayout(sidebar); layout.setContentsMargins(16, 24, 16, 18); layout.setSpacing(3)
        brand = QLabel("◈ PQC\nSECURITY TOOLKIT"); brand.setStyleSheet("font-size: 17px; font-weight: 700; line-height: 1.4; margin: 0 0 24px 8px;"); layout.addWidget(brand)
        groups = [("OVERVIEW", [("Dashboard", "dashboard")]), ("CRYPTOGRAPHY", [("ML-KEM", "kem"), ("Digital Signatures", "signatures"), ("Secure Files", "files")]), ("ANALYSIS", [("Benchmark", "benchmark"), ("Comparison", "comparison")]), ("LEARN", [("PQC Concepts", "education")]), ("SYSTEM", [("Settings", "settings"), ("About", "about")])]
        for heading, items in groups:
            label = QLabel(heading); label.setObjectName("eyebrow"); label.setStyleSheet("margin: 15px 8px 5px;"); layout.addWidget(label)
            for text, key in items:
                button = NavButton(text); button.activated.connect(lambda target=key: self.show_page(target)); self.nav_buttons[key] = button; layout.addWidget(button)
        layout.addStretch(); footer = QLabel("Experimental security research\nProvider-backed operations only"); footer.setStyleSheet("color: #64748b; font-size: 11px; margin: 8px;"); layout.addWidget(footer); return sidebar

    def _register_pages(self) -> None:
        store = BenchmarkStore(Path(__file__).resolve().parents[1] / "data" / "benchmark_results.json")
        page_objects = {"dashboard": DashboardPage(self.backend_available), "kem": KEMPage(), "signatures": SignaturesPage(), "files": FileSecurityPage(), "benchmark": BenchmarkPage(store), "comparison": ComparisonPage(), "education": EducationPage(), "settings": SettingsPage(), "about": AboutPage()}
        for key, page in page_objects.items():
            page_objects[key].notify.connect(self.show_notification) if hasattr(page_objects[key], "notify") else None
            if key == "dashboard": page.navigate.connect(self.show_page)
            scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.Shape.NoFrame); scroll.setWidget(page); self.pages[key] = scroll; self.stack.addWidget(scroll)

    def show_page(self, key: str) -> None:
        if key not in self.pages: return
        self.stack.setCurrentWidget(self.pages[key]); self.module_title.setText(self.nav_buttons[key].text() if key in self.nav_buttons else "Dashboard")
        for button_key, button in self.nav_buttons.items(): button.setProperty("active", button_key == key); button.style().unpolish(button); button.style().polish(button)

    def show_notification(self, message: str, success: bool) -> None: self.toast.show_message(message, success)

    def update_metrics(self) -> None:
        status = "● Backend Ready" if self.backend_available else "● Backend Limited"
        cpu = f"CPU {psutil.cpu_percent():.0f}%" if psutil else "CPU n/a"; memory = f"RAM {psutil.virtual_memory().percent:.0f}%" if psutil else "RAM n/a"; self.system_status.setText(f"{status}    {cpu}    {memory}"); self.system_status.setStyleSheet(f"color: {'#22c55e' if self.backend_available else '#f59e0b'};")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event); self.toast.setGeometry(30, 75, 420, 44)
