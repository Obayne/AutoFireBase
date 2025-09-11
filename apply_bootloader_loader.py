# apply_bootloader_loader.py
# Ensures app is a package and makes boot.py load app/main.py by filepath if import fails.

from pathlib import Path
import datetime

ROOT = Path(".")
APP = ROOT / "app"
APP_INIT = APP / "__init__.py"
BOOT = APP / "boot.py"

def backup(p: Path):
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        p.with_suffix(p.suffix + f".bak_{ts}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

LOADER_BOOT = r'''# boot.py — robust loader
import os, sys, traceback, datetime, importlib

from PySide6 import QtWidgets

def _log_startup_error(text: str) -> str:
    base = os.path.join(os.path.expanduser("~"), "AutoFire", "logs")
    os.makedirs(base, exist_ok=True)
    path = os.path.join(base, f"startup_error_{datetime.datetime.now():%Y%m%d_%H%M%S}.log")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass
    return path

def _load_app_main():
    # 1) normal import
    try:
        return importlib.import_module("app.main")
    except Exception:
        pass

    # 2) file-based import from likely locations
    candidates = []
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)
    meipass = getattr(sys, "_MEIPASS", None)

    for base in (exe_dir, meipass, os.path.dirname(__file__)):
        if not base: continue
        candidates += [
            os.path.join(base, "_internal", "app", "main.py"),
            os.path.join(base, "app", "main.py"),
        ]

    for path in candidates:
        if os.path.exists(path):
            try:
                import importlib.util, types
                spec = importlib.util.spec_from_file_location("app.main", path)
                mod = importlib.util.module_from_spec(spec)  # type: ignore
                assert spec and spec.loader
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                sys.modules["app.main"] = mod
                return mod
            except Exception:
                continue

    # give up
    raise ModuleNotFoundError("app.main")

def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    try:
        m = _load_app_main()
        create_window = getattr(m, "create_window", None)
        if callable(create_window):
            win = create_window()
            win.show()
            app.exec()
            return

        # fallback UI if create_window not present
        from PySide6 import QtWidgets as _W
        wf = _W.QMainWindow()
        wf.setWindowTitle("Auto-Fire — Fallback UI")
        lab = _W.QLabel("Fallback loaded (app.main missing create_window).")
        lab.setMargin(16); wf.setCentralWidget(lab); wf.resize(900, 600); wf.show()
        app.exec()
    except Exception:
        tb = traceback.format_exc()
        p = _log_startup_error(tb)
        QtWidgets.QMessageBox.critical(None, "Startup Error", f"{tb}\n\nSaved: {p}")

if __name__ == "__main__":
    main()
'''

# 1) make sure app/ is a package
APP.mkdir(parents=True, exist_ok=True)
if not APP_INIT.exists():
    APP_INIT.write_text("# package marker\n", encoding="utf-8")
    print("created", APP_INIT)
else:
    print("ok:", APP_INIT)

# 2) replace boot.py with robust loader
backup(BOOT)
BOOT.write_text(LOADER_BOOT, encoding="utf-8")
print("wrote loader to", BOOT)

print("Done.")
