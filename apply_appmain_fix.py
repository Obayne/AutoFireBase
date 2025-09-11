# apply_appmain_fix.py
# Fixes startup: ensures app/__init__.py, app/main.py has create_window(),
# app/minwin.py fallback exists, and AutoFire.spec has required hiddenimports.

from pathlib import Path
import re, datetime

ROOT = Path(".")
APP = ROOT / "app"
APP_INIT = APP / "__init__.py"
MAIN = APP / "main.py"
MINWIN = APP / "minwin.py"
SPEC = ROOT / "AutoFire.spec"

def backup(p: Path):
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        p.with_suffix(p.suffix + f".bak_{ts}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# 1) app/__init__.py  (turn app into a proper package)
APP.mkdir(parents=True, exist_ok=True)
if not APP_INIT.exists():
    APP_INIT.write_text("# package marker\n", encoding="utf-8")
    print("created", APP_INIT)
else:
    print("ok:", APP_INIT)

# 2) Ensure app/main.py exists and provides create_window()
if not MAIN.exists():
    MAIN.write_text(
        """from PySide6.QtWidgets import QApplication, QMainWindow
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
""", encoding="utf-8")
    print("created minimal", MAIN)
else:
    txt = MAIN.read_text(encoding="utf-8")
    # If it doesn't expose create_window(), add a tiny factory.
    if "def create_window" not in txt:
        backup(MAIN)
        txt += """

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
        MAIN.write_text(txt, encoding="utf-8")
        print("patched", MAIN, "to add create_window()")
    else:
        print("ok: create_window() already present in", MAIN)

# 3) Minimal fallback window (if main fails)
if not MINWIN.exists():
    MINWIN.write_text(
        """from PySide6 import QtWidgets
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
""", encoding="utf-8")
    print("created", MINWIN)
else:
    print("ok:", MINWIN)

# 4) Ensure AutoFire.spec includes hiddenimports so PyInstaller always bundles modules
if SPEC.exists():
    s = SPEC.read_text(encoding="utf-8")
    if "hiddenimports" in s:
        # Replace the list contents with a known-good set
        s2 = re.sub(
            r"hiddenimports\s*=\s*\[[^\]]*\]",
            ("hiddenimports=["
             "'app','app.main','app.minwin','app.scene','app.device','app.catalog',"
             "'app.tools','app.tools.array','app.tools.draw','app.tools.dimension',"
             "'core.logger','core.error_hook','core.logger_bridge','updater.auto_update'"+
             "]"),
            s, count=1
        )
        if s2 != s:
            backup(SPEC)
            SPEC.write_text(s2, encoding="utf-8")
            print("patched hiddenimports in", SPEC)
        else:
            print("ok: hiddenimports present in", SPEC)
    else:
        # Insert hiddenimports argument into the Analysis(…) call
        s2 = re.sub(
            r"Analysis\(",
            ("Analysis(hiddenimports=["
             "'app','app.main','app.minwin','app.scene','app.device','app.catalog',"
             "'app.tools','app.tools.array','app.tools.draw','app.tools.dimension',"
             "'core.logger','core.error_hook','core.logger_bridge','updater.auto_update'"
             "], "),
            s, count=1
        )
        if s2 != s:
            backup(SPEC)
            SPEC.write_text(s2, encoding="utf-8")
            print("injected hiddenimports into", SPEC)
        else:
            print("NOTE: could not find Analysis(…) in spec to inject hiddenimports.")
else:
    print("WARNING: AutoFire.spec not found; build will still work, but bundling may be incomplete.")

print("Done.")
