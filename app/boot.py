<<<<<<< Updated upstream
# app/boot.py — dynamic entry, resilient to missing create_window
import os, sys, traceback, time, importlib

# Ensure project root is on sys.path when running from source
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# In frozen EXE, include PyInstaller's _MEIPASS if present
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass and meipass not in sys.path:
        sys.path.insert(0, meipass)

def log_startup_error(msg: str):
=======
# boot.py — robust loader
# Some helpful error messages and dynamically generated content can be long.
# Allow E501 for this file to reduce noisy line-length warnings from Ruff.
# ruff: noqa: E501
# noqa: E501
import os, sys, traceback, datetime, importlib
from PySide6 import QtWidgets

def _log_startup_error(text: str) -> str:
    base = os.path.join(os.path.expanduser('~'), 'AutoFire', 'logs')
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
>>>>>>> Stashed changes
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception:
        pass
    return path

<<<<<<< Updated upstream
def resolve_create_window():
    """Return a callable that builds the main window."""
    main_mod = importlib.import_module("app.main")
    # Preferred: explicit factory
    cw = getattr(main_mod, "create_window", None)
    if callable(cw):
        return cw
    # Fallback: direct MainWindow construction
    MW = getattr(main_mod, "MainWindow", None)
    if MW is not None:
        def _cw():
            return MW()
        return _cw
    # Nothing suitable found
    raise ImportError(
        "app.main has neither 'create_window()' nor 'MainWindow'. "
        f"Found: {', '.join([n for n in dir(main_mod) if not n.startswith('_')])}"
    )

def main():
    try:
        from PySide6 import QtWidgets
    except Exception:
        log_startup_error(traceback.format_exc())
        raise

=======
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
        if not base:
            continue
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
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
        log_startup_error(tb)
        # Show a visible fallback window so you know it failed
        app = QtWidgets.QApplication([])
        w = QtWidgets.QWidget()
        from PySide6 import QtCore
        w.setWindowTitle("Auto-Fire (fallback)")
        w.resize(600, 320)
        lab = QtWidgets.QLabel(
            "Main UI failed to load.\n\n"
            "See latest file in ~/AutoFire/logs for details.\n"
            "Tip: ensure app/main.py defines create_window() or a MainWindow class."
        )
        lab.setAlignment(QtCore.Qt.AlignCenter)
        lay = QtWidgets.QVBoxLayout(w); lay.addWidget(lab)
        w.show(); app.exec()
        return

    # Normal path
    app = QtWidgets.QApplication([])
    win = create_window()
    win.show()
    app.exec()

if __name__ == "__main__":
=======
        p = _log_startup_error(tb)
        QtWidgets.QMessageBox.critical(None, 'Startup Error', f'{tb}\n\nSaved: {p}')

if __name__ == '__main__':
>>>>>>> Stashed changes
    main()
