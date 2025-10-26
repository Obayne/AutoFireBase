#!/usr/bin/env python3
"""
Clone a minimal source tree into unified_app/src based on logs/used_files_manifest.json.
Preserves relative directory structure.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "logs" / "used_files_manifest.json"
DEST_ROOT = REPO_ROOT / "unified_app" / "src"


def copy_files(files: List[str], dry_run: bool = False) -> int:
    count = 0
    for rel in files:
        src = (REPO_ROOT / rel).resolve()
        if not src.exists():
            print(f"[skip] missing: {rel}")
            continue
        dest = (DEST_ROOT / rel).resolve()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dry_run:
            print(f"[dry-run] copy {src} -> {dest}")
        else:
            shutil.copy2(src, dest)
        count += 1
    return count


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Print actions without copying")
    args = ap.parse_args(argv)

    if not MANIFEST.exists():
        print(f"Manifest not found: {MANIFEST}")
        return 2

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = data.get("files", [])
    DEST_ROOT.mkdir(parents=True, exist_ok=True)

    copied = copy_files(files, dry_run=args.dry_run)
    print(f"Copied {copied} files to {DEST_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
