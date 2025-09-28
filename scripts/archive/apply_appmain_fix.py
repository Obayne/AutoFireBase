# apply_appmain_fix.py
# Fixes startup: ensures app/__init__.py, app/main.py has create_window(),
# app/minwin.py fallback exists, and AutoFire.spec has required hiddenimports.

import datetime
import logging
import re
from pathlib import Path

from app.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

ROOT = Path(".")
APP = ROOT / "app"
APP_INIT = APP / "__init__.py"
MAIN = APP / "main.py"
MINWIN = APP / "minwin.py"
SPEC = ROOT / "AutoFire.spec"


def backup(p: Path) -> None:
    """Create a timestamped backup of the path if it exists."""
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bak = p.with_suffix(p.suffix + f".bak_{ts}")
        bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")


def ensure_package() -> None:
    APP.mkdir(parents=True, exist_ok=True)
    if not APP_INIT.exists():
        APP_INIT.write_text("# package marker\n", encoding="utf-8")
        logger.info("created %s", APP_INIT)
    else:
        logger.debug("ok: %s exists", APP_INIT)


def ensure_main() -> None:
    minimal = """from PySide6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto-Fire — minimal main")


def create_window():
    return MainWindow()


def main():
    app = QApplication([])
    w = create_window()
    w.show()
    app.exec()
"""

    if not MAIN.exists():
        MAIN.write_text(minimal, encoding="utf-8")
        logger.info("created minimal %s", MAIN)
        return

    # If MAIN exists, ensure it exposes create_window(). If not, append a simple factory.
    txt = MAIN.read_text(encoding="utf-8")
    if "def create_window" not in txt:
        backup(MAIN)
        logger.info("patching %s to add create_window() factory", MAIN)
        addition = """
# Added by apply_appmain_fix: factory for boot.py
try:
    _MW = MainWindow  # type: ignore[name-defined]

    def create_window():
        return _MW()
except Exception:
    # Fallback: if no MainWindow class name, just create a generic window.
    from PySide6.QtWidgets import QMainWindow


    def create_window():
        return QMainWindow()
"""
        MAIN.write_text(txt + addition, encoding="utf-8")
        logger.info("patched %s", MAIN)
    else:
        logger.debug("ok: create_window() already present in %s", MAIN)


def ensure_minwin() -> None:
    fallback = """from PySide6 import QtWidgets

def run_minimal():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    w = QtWidgets.QMainWindow()
    w.setWindowTitle("Auto-Fire — Minimal Window (Fallback)")
    lab = QtWidgets.QLabel("Fallback window loaded. If you see this, main UI didn't start.")
    lab.setMargin(16)
    w.setCentralWidget(lab)
    w.resize(900, 600)
    w.show()
    if not QtWidgets.QApplication.instance().startingUp():
        app.exec()
"""

    if not MINWIN.exists():
        MINWIN.write_text(fallback, encoding="utf-8")
        logger.info("created %s", MINWIN)


def ensure_spec_hiddenimports() -> None:
    if not SPEC.exists():
        logger.warning("AutoFire.spec not found; skipping hiddenimports patch.")
        return

    s = SPEC.read_text(encoding="utf-8")
    hidden_list = (
        "'app','app.main','app.minwin','app.scene','app.device','app.catalog',"
        "'app.tools','app.tools.array','app.tools.draw','app.tools.dimension',"
        "'core.logger','core.error_hook','core.logger_bridge','updater.auto_update'"
    )

    if "hiddenimports" in s:
        s2 = re.sub(r"hiddenimports\s*=\s*\[[^\]]*\]", f"hiddenimports=[{hidden_list}]", s, count=1)
        if s2 != s:
            backup(SPEC)
            SPEC.write_text(s2, encoding="utf-8")
            logger.info("patched hiddenimports in %s", SPEC)
        else:
            logger.debug("hiddenimports already present and unchanged in %s", SPEC)
        return

    # Attempt to inject into Analysis(…) call
    s2 = re.sub(r"Analysis\(", f"Analysis(hiddenimports=[{hidden_list}], ", s, count=1)
    if s2 != s:
        backup(SPEC)
        SPEC.write_text(s2, encoding="utf-8")
        logger.info("injected hiddenimports into %s", SPEC)
    else:
        logger.warning("Could not find Analysis(...) in spec to inject hiddenimports.")


def main_entry() -> None:
    ensure_package()
    ensure_main()
    ensure_minwin()
    ensure_spec_hiddenimports()
    logger.info("apply_appmain_fix completed")


if __name__ == "__main__":
    main_entry()
