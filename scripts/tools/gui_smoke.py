"""Lightweight GUI triage smoke test.

Run with the project venv to detect import-time regressions in GUI and cad_core modules.
Exits with code 0 if all imports succeed; non-zero otherwise and prints tracebacks.
"""

import sys
import traceback
from pathlib import Path

# Ensure repo root is on sys.path so top-level packages import correctly when
# this script is run from scripts/tools
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

modules = [
    "app",
    "app.boot",
    "app.main",
    "frontend",
    "backend",
    "cad_core",
    "tools",
    "run_logs",
]
ok = []
fail = []
for m in modules:
    try:
        __import__(m)
        ok.append(m)
    except Exception:
        fail.append((m, traceback.format_exc()))
print("IMPORT_OK:", ok)
print("IMPORT_FAIL_COUNT:", len(fail))
for name, tb in fail:
    print("\n--- FAIL:", name)
    print(tb)
sys.exit(0 if not fail else 2)
