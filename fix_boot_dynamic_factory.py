# fix_boot_dynamic_factory.py
# Make app/boot.py resilient: it will use app.main.create_window if present,
# otherwise instantiate app.main.MainWindow.

import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOOT = ROOT / "app" / "boot.py"
STAMP = time.strftime("%Y%m%d_%H%M%S")

CODE = r'''# app/boot.py — dynamic entry, resilient to missing create_window
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
    try:
        base = os.path.join(os.path.expanduser("~"), "AutoFire", "logs")
        os.makedirs(base, exist_ok=True)
        stamp = time.strftime("%Y%m%d_%H%M%S")
        p = os.path.join(base, f"startup_error_{stamp}.log")
        with open(p, "w", encoding="utf-8") as f:
            f.write("Startup error:\n\n" + msg + "\n")
        return p
    except Exception:
        return None

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

    try:
        create_window = resolve_create_window()
    except Exception:
        tb = traceback.format_exc()
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
    main()
'''


def main():
    BOOT.parent.mkdir(parents=True, exist_ok=True)
    if BOOT.exists():
        bkp = BOOT.with_suffix(".py.bak-" + STAMP)
        bkp.write_text(BOOT.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        print(f"[backup] {bkp}")
    BOOT.write_text(CODE, encoding="utf-8")
    print(f"[write]  {BOOT}")
    print("\nDone. Launch with:  py -3 -m app.boot")


if __name__ == "__main__":
    main()
