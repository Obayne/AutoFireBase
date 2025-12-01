"""Resolve conflict markers in a short list of files by preferring the
stashed/local section.

This script is intentionally small and safe: it backs up each file before
rewriting. Usage:
    python scripts/tools/resolve_specific_conflicts.py
"""

from pathlib import Path


def _split_conflict_blocks(text: str) -> tuple[bool, str]:
    """Return (changed, new_text). Keeps section between '=======' and '>>>>>>>'
    (the stashed/local side). If malformed conflict markers are found, returns
    (False, original_text) to avoid partial edits.
    """
    out_parts: list[str] = []
    i = 0
    changed = False
    while True:
        s = text.find("<<<<<<<", i)
        if s == -1:
            out_parts.append(text[i:])
            break
        changed = True
        out_parts.append(text[i:s])
        e = text.find("=======", s)
        if e == -1:
            return False, text
        g = text.find(">>>>>>>", e)
        if g == -1:
            return False, text
        # keep the stashed/local section
        out_parts.append(text[e + len("=======") : g])
        i = g + len(">>>>>>>")
    return changed, "".join(out_parts)


def rewrite_file(fp: Path) -> bool:
    try:
        txt = fp.read_text(encoding="utf-8")
    except Exception:
        return False
    changed, new = _split_conflict_blocks(txt)
    if not changed:
        return True
    bak = fp.with_suffix(fp.suffix + ".bak-conflict-resolve")
    bak.write_text(txt, encoding="utf-8")
    fp.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    files = [Path("app/main.py"), Path("app/boot.py")]
    for fp in files:
        if not fp.exists():
            print(f"skip: {fp} (not found)")
            continue
        ok = rewrite_file(fp)
        print(f"{fp}: {'rewritten' if ok else 'skipped/failed'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
