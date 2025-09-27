@'
from pathlib import Path
<<<<<<< Updated upstream
import re, datetime
=======
import logging

_logger = logging.getLogger(__name__)

# This helper writes embedded code strings (long lines); allow E501 here.
# ruff: noqa: E501
# noqa: E501
>>>>>>> Stashed changes

ROOT = Path(".")
APP = ROOT/"app"
INIT = APP/"__init__.py"
MAIN = APP/"main.py"
BOOT = APP/"boot.py"

def backup(p: Path):
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        p.with_suffix(p.suffix + f".bak_{ts}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# 1) app/__init__.py
APP.mkdir(parents=True, exist_ok=True)
if not INIT.exists():
    INIT.write_text("# package marker\n", encoding="utf-8")
    _logger.info("created %s", INIT)
else:
    _logger.info("ok: %s", INIT)

# 2) ensure main.py exists and exports create_window()
if not MAIN.exists():
    MAIN.write_text(
        "from PySide6.QtWidgets import QApplication, QMainWindow\n"
        "class MainWindow(QMainWindow):\n"
        "    def __init__(self):\n"
        "        super().__init__()\n"
        "        self.setWindowTitle('Auto-Fire — minimal main')\n"
        "def create_window():\n"
        "    return MainWindow()\n"
        "def main():\n"
        "    app = QApplication([])\n"
        "    w = create_window(); w.show(); app.exec()\n",
        encoding="utf-8",
    )
    _logger.info("created minimal %s", MAIN)
else:
    txt = MAIN.read_text(encoding="utf-8")
    if "def create_window" not in txt:
        backup(MAIN)
        # If a class called MainWindow exists, add a simple factory at the end.
        add = "\n\n# added by repair_entrypoints\ntry:\n    _MW = MainWindow\n    def create_window():\n        return _MW()\nexcept Exception:\n    from PySide6.QtWidgets import QMainWindow\n    def create_window():\n        return QMainWindow()\n"
        MAIN.write_text(txt + add, encoding="utf-8")
        _logger.info("patched %s to add create_window()", MAIN)
    else:
        _logger.info("ok: create_window() present")

# 3) robust boot loader that can import from files in app/ even if not packaged as code
boot_code = r"""# boot.py — robust loader
import os, sys, traceback, datetime, importlib
from PySide6 import QtWidgets

def _log_startup_error(text: str) -> str:
    base = os.path.join(os.path.expanduser('~'), 'AutoFire', 'logs')
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception:
        pass
    return path

def _load_app_main():
    # Try normal import first (works if PyInstaller bundled the package)
    try:
        return importlib.import_module('app.main')
    except Exception:
        pass

    # Try file-based import from common locations
    candidates = []
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    meipass = getattr(sys, '_MEIPASS', None)

    for base in [exe_dir, meipass, os.path.dirname(__file__)]:
        if not base: continue
        candidates += [
            os.path.join(base, '_internal', 'app', 'main.py'),
            os.path.join(base, 'app', 'main.py'),
        ]

    for path in candidates:
        if path and os.path.exists(path):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location('app.main', path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                    sys.modules['app.main'] = mod
                    return mod
            except Exception:
                continue

    raise ModuleNotFoundError('app.main')

def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    try:
        m = _load_app_main()
        create_window = getattr(m, 'create_window', None)
        if callable(create_window):
            w = create_window(); w.show(); app.exec(); return

        # Fallback UI
        w = QtWidgets.QMainWindow()
        w.setWindowTitle('Auto-Fire — Fallback UI (no create_window)')
        lab = QtWidgets.QLabel('Fallback window loaded.')
        lab.setMargin(16); w.setCentralWidget(lab); w.resize(900, 600); w.show()
        app.exec()
    except Exception:
        tb = traceback.format_exc()
        p = _log_startup_error(tb)
        QtWidgets.QMessageBox.critical(None, 'Startup Error', f'{tb}\n\nSaved: {p}')

if __name__ == '__main__':
    main()
"""
backup(BOOT)
<<<<<<< Updated upstream
BOOT.write_text(boot_code, encoding='utf-8')
print("wrote", BOOT)

print("Done.")
'@ | Set-Content -Encoding UTF8 .\repair_entrypoints.py
=======
BOOT.write_text(boot_code, encoding="utf-8")
_logger.info("wrote %s", BOOT)

_logger.info("Done.")
>>>>>>> Stashed changes
