"""
Creates backups with suffix '.bak-strip-stashed'.

Run from repo root with the repo Python:
    & .venv/Scripts/python.exe scripts/tools/strip_stashed_markers.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", ".venv", "build", "dist", "node_modules", "__pycache__"}


def _strip_markers(text: str) -> list[str]:
    """Return a list of lines with obvious git stash/merge markers removed.

    This is intentionally conservative: if we detect a conflict marker block we
    leave the file untouched (caller can inspect the .bak file). We do remove
    literal 'Stashed changes' summary lines that some tools paste into files.
    """
    out: list[str] = []
    for ln in text.splitlines():
        s = ln.strip()
        if (
            s.startswith("<<<<<<<")
            or s.startswith("=======")
            or s.startswith(">>>>>>>>")
        ):
            # don't try to auto-resolve real conflict blocks here
            return []
        if "Stashed changes" in ln or "stash" in ln.lower():
            # drop these lines
            continue
        out.append(ln)
    return out


changed = []
for p in ROOT.rglob("*"):
    if p.is_dir():
        parts = set(p.parts)
        if parts & EXCLUDE:
            continue
        continue
    if any(part in EXCLUDE for part in p.parts):
        continue
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        continue
    new_lines = _strip_markers(txt)
    # empty list means we chose to skip because a conflict marker was detected
    if not new_lines:
        continue
    lines = txt.splitlines()
    if new_lines == lines:
        continue
    bak = p.with_suffix(p.suffix + ".bak-strip-stashed")
    bak.write_text(txt, encoding="utf-8")
    p.write_text("\n".join(new_lines) + ("\n" if txt.endswith("\n") else ""), encoding="utf-8")
    changed.append(str(p))

print(f"Stripped marker from {len(changed)} files")
for c in changed:
    print(f" - {c}")
sys.exit(0)
