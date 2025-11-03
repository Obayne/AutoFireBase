#!/usr/bin/env python3
"""
Verify that importing the v1 beta entry from unified_app/src does not pull in
any modules from the legacy repository root outside the sandbox.

Exit codes:
 0 - OK (no legacy imports)
 1 - Failure (legacy file(s) found in sys.modules)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_SRC = REPO_ROOT / "unified_app" / "src"


def collect_legacy_imports() -> List[Tuple[str, Path]]:
    offenders: List[Tuple[str, Path]] = []
    for name, mod in list(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        # Consider any repo-root file that is NOT under sandbox src as legacy
        try:
            p.relative_to(REPO_ROOT)
        except Exception:
            continue
        try:
            p.relative_to(SANDBOX_SRC)
            # under sandbox -> OK
            continue
        except Exception:
            offenders.append((name, p))
    return offenders


def main() -> int:
    if not SANDBOX_SRC.exists():
        print(f"Sandbox src not found: {SANDBOX_SRC}")
        return 1

    # Strict PYTHONPATH to sandbox first
    sys.path.insert(0, str(SANDBOX_SRC))
    os.environ.setdefault("AUTOFIRE_NO_SPLASH", "1")

    # Import entry
    try:
        import autofire_professional_integrated  # noqa: F401
    except Exception as e:  # noqa: BLE001
        print(f"Import failed: {e}")
        return 1

    offenders = collect_legacy_imports()
    if offenders:
        print("Legacy imports detected (outside unified_app/src):")
        for name, path in offenders:
            print(f" - {name}: {path}")
        return 1

    print("Isolation OK: no legacy imports loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
