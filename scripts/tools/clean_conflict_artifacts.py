"""
Clean leftover merge artifact lines from specific files.
Backs up each file to <file>.bak-conflict-clean before modifying.

Usage:
    & .venv/Scripts/python.exe scripts/tools/clean_conflict_artifacts.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [Path.cwd() / "app" / "main.py"]

pattern = re.compile(r"^\s*(?:<{7}.*|>{7}.*|={7,}|Stashed changes|Updated upstream)\s*$")

changed = []
for fp in TARGETS:
    if not fp.exists():
        print(f"skip: {fp} not found")
        continue
    txt = fp.read_text(encoding="utf-8")
    lines = txt.splitlines()
    new_lines = [ln for ln in lines if not pattern.match(ln)]
    if new_lines == lines:
        print(f"no artifacts in {fp}")
        continue
    bak = fp.with_suffix(fp.suffix + ".bak-conflict-clean")
    bak.write_text(txt, encoding="utf-8")
    fp.write_text("\n".join(new_lines) + ("\n" if txt.endswith("\n") else ""), encoding="utf-8")
    changed.append(str(fp))

print(f"Cleaned {len(changed)} files:")
for c in changed:
    print(" -", c)
