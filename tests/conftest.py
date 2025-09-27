import os
import sys
from pathlib import Path


def _ensure_repo_root_on_path() -> None:
    # Add repository root to sys.path so `backend`, `frontend`, `cad_core` are importable.
    tests_dir = Path(__file__).resolve().parent
    repo_root = tests_dir.parent
    repo_str = str(repo_root)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)


_ensure_repo_root_on_path()


# Provide a minimal Qt application for any modules that import PySide6.
# This prevents errors like "QFontDatabase: Must construct a QGuiApplication..."
# when Qt types get touched during import in headless CI.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6 import QtWidgets  # type: ignore

    _qt_app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
except Exception:
    # If PySide6 is not installed for test env, ignore.
    _qt_app = None
