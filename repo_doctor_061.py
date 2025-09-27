# repo_doctor_061.py
# Fixes "minimal window" by ensuring packages & import path are correct.
# Safe to run multiple times.

<<<<<<< Updated upstream
import sys, os, textwrap, time
=======
# This file embeds a large BOOT_SAFE string and long help messages; allow
# E501 here to avoid noisy line-length warnings from Ruff.
# ruff: noqa: E501
# noqa: E501

import sys
import time
>>>>>>> Stashed changes
from pathlib import Path
import logging

_logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent
APP  = ROOT / "app"
CORE = ROOT / "core"
TOOLS= APP / "tools"
UPD  = ROOT / "updater"

REQ_DIRS = [APP, CORE, TOOLS, UPD]
NEEDED_INITS = [d / "__init__.py" for d in REQ_DIRS]

BOOT = APP / "boot.py"

BOOT_SAFE = r'''# app/boot.py — hardened entry that avoids "minimal window" fallback surprises.
import os, sys, traceback, time

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

def main():
    try:
        from PySide6 import QtWidgets
    except Exception as ex:
        path = log_startup_error(traceback.format_exc())
        raise

    try:
        from app.main import create_window
    except Exception:
        # Log full traceback, then show a minimal window so you see *something*
        tb = traceback.format_exc()
        log_startup_error(tb)
        # Minimal window
        app = QtWidgets.QApplication([])
        w = QtWidgets.QWidget()
        w.setWindowTitle("Auto-Fire (fallback)")
        w.resize(520, 260)
        from PySide6 import QtCore, QtGui
        lab = QtWidgets.QLabel("Main UI failed to load.\n\nSee latest file in ~/AutoFire/logs for details.\n"
                               "Run:  py -3 -m app.boot  from repo root\n"
                               "to surface import errors in the console.")
        lab.setAlignment(QtCore.Qt.AlignCenter)
        lay = QtWidgets.QVBoxLayout(w); lay.addWidget(lab)
        w.show(); app.exec()
        return

    # Normal path
    app = QtWidgets.QApplication([])
    w = create_window()
    w.show()
    app.exec()

if __name__ == "__main__":
    main()
'''

def ensure_inits():
    made = []
    for init in NEEDED_INITS:
        if not init.exists():
            init.parent.mkdir(parents=True, exist_ok=True)
            init.write_text("# package marker\n", encoding="utf-8")
            made.append(init)
    return made

def maybe_patch_boot():
    # Only overwrite if missing or obviously not hardened
    need = (not BOOT.exists())
    if not need:
        txt = BOOT.read_text(encoding="utf-8", errors="ignore")
        need = ("from app.main import create_window" not in txt) or ("log_startup_error" not in txt)
    if need:
        if BOOT.exists():
                bkp = BOOT.with_suffix(".py.bak-" + time.strftime("%Y%m%d_%H%M%S"))
                bkp.write_text(BOOT.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                _logger.info("[backup] %s", bkp)
        BOOT.write_text(BOOT_SAFE, encoding="utf-8")
        return True
    return False

def main():
    _logger.info("== AutoFireBase Repo Doctor v0.6.1 ==")
    _logger.info("Root: %s", ROOT)

    missing_dirs = [d for d in REQ_DIRS if not d.exists()]
    if missing_dirs:
        for d in missing_dirs:
            _logger.warning("[warn] missing directory: %s", d)
        _logger.info("Create those folders (even empty) to keep Python imports clean.")

    made_inits = ensure_inits()
    for p in made_inits:
        _logger.info("[init] created: %s", p.relative_to(ROOT))

    changed_boot = maybe_patch_boot()
    if changed_boot:
<<<<<<< Updated upstream
        print(f"[patch] wrote hardened: app/boot.py")
=======
        _logger.info("[patch] wrote hardened: app/boot.py")
>>>>>>> Stashed changes
    else:
        _logger.info("[ok] app/boot.py already hardened")

    # quick sanity: can we import app.main?
    sys.path.insert(0, str(ROOT))
    try:
        __import__("app.main")
        _logger.info("[ok] import app.main -> success")
    except Exception as ex:
        _logger.error("[fail] import app.main -> %s", ex)

    # show tips
    _logger.info("\nNext:")
    _logger.info("  1) Run the app from source to see real errors:")
    _logger.info("       py -3 -m app.boot")
    _logger.info("  2) If it still falls back, open newest file in:")
    _logger.info("       %USERPROFILE%\\AutoFire\\logs\\startup_error_*.log")
    _logger.info("     and paste the latest traceback here.")

if __name__ == "__main__":
    main()
