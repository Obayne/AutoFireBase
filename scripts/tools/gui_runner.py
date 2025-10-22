"""Automated GUI runner: create MainWindow, exercise key flows, then quit.

This runs headless enough (no user interaction) by scheduling actions via QTimer.
It will exit on its own. Run with the project venv python.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.main import MainWindow  # noqa: E402 (we adjust sys.path above intentionally)
from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402


def safe_call(win, name):
    try:
        fn = getattr(win, name)
    except Exception:
        print(f"MISSING: {name}")
        return
    try:
        print(f"CALL: {name}")
        fn()
    except TypeError:
        # some methods require parameters; try common safe variants
        try:
            fn(False)
        except Exception as e:
            print(f"ERR calling {name}: {e}")
    except Exception as e:
        print(f"ERR calling {name}: {e}")


def run_sequence():
    app = QApplication([])
    win = MainWindow()
    win.show()

    actions = [
        (200, lambda: safe_call(win, "toggle_grid")),
        (400, lambda: safe_call(win, "toggle_snap")),
        (600, lambda: safe_call(win, "toggle_crosshair")),
        (800, lambda: safe_call(win, "toggle_coverage")),
        (1000, lambda: safe_call(win, "toggle_placement_coverage")),
        (1200, lambda: safe_call(win, "_init_sheet_manager")),
        (1400, lambda: safe_call(win, "_apply_snap_step_from_inches")),
        # Switch paper/model space
        (1600, lambda: win.toggle_paper_space(True)),
        (1800, lambda: win.toggle_paper_space(False)),
        # Start and stop a couple of tools if present
        (2000, lambda: safe_call(win, "start_dimension")),
        (2200, lambda: safe_call(win, "finish_trim")),
        (2400, lambda: safe_call(win, "start_text")),
        (2600, lambda: safe_call(win, "start_mtext")),
        # final checks
        (3000, lambda: print("SMOKE_DONE")),
        (3200, lambda: win.close()),
        (3500, lambda: app.quit()),
    ]

    for ms, cb in actions:
        QTimer.singleShot(ms, cb)

    app.exec()


if __name__ == "__main__":
    run_sequence()
