#!/usr/bin/env python3
"""
Generate a manifest of Python source files used by one or more entry scripts,
without executing application logic (static import graph via modulefinder).

Outputs logs/used_files_manifest.json with a list of repo-relative file paths.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from modulefinder import ModuleFinder
from pathlib import Path
from typing import Iterable, List, Set

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENTRIES = ["main.py", "autofire_professional_integrated.py"]


def existing_entries(entries: Iterable[str]) -> List[Path]:
    out: List[Path] = []
    for e in entries:
        p = (REPO_ROOT / e).resolve()
        if p.exists():
            out.append(p)
    return out


def run_modulefinder(entry_files: List[Path]) -> Set[Path]:
    found: Set[Path] = set()
    if not entry_files:
        return found

    # Ensure repo root is importable for absolute imports like `frontend.*`
    sys.path.insert(0, str(REPO_ROOT))

    finder = ModuleFinder(path=[str(REPO_ROOT)] + sys.path)

    for entry in entry_files:
        try:
            finder.run_script(str(entry))
        except (ImportError, SyntaxError, OSError, RuntimeError) as exc:
            # We intentionally avoid failing hard: static analysis can hit guarded imports
            print(f"[warn] modulefinder raised for {entry.name}: {exc}", file=sys.stderr)

    for _name, mod in finder.modules.items():
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        fpath = Path(f)
        # Only include project files under repo root; skip venv/site-packages/stdlib etc.
        try:
            rel = fpath.resolve().relative_to(REPO_ROOT)
        except ValueError:
            continue
        if rel.suffix == ".py" and not any(part == ".venv" for part in rel.parts):
            found.add(rel)

    return found


def write_manifest(files: Iterable[Path], entries: List[Path]) -> Path:
    ts = time.strftime("%Y-%m-%dT%H-%M-%S")
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_path = logs_dir / "used_files_manifest.json"

    data: dict[str, object] = {
        "generated_at": ts,
        "repo_root": str(REPO_ROOT),
        "entries": [str(p.relative_to(REPO_ROOT)) for p in entries],
        "files": sorted(str(p).replace("\\", "/") for p in files),
    }

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out_path


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--entry",
        action="append",
        dest="entries",
        help="Entry script relative to repo root (can be repeated). Default: main.py + autofire_professional_integrated.py",
    )
    args = ap.parse_args(argv)

    entries = existing_entries(args.entries if args.entries else DEFAULT_ENTRIES)
    files = run_modulefinder(entries)
    out = write_manifest(files, entries)
    print(f"Wrote manifest: {out}")
    print(f"Files discovered: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
