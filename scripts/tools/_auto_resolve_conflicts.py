"""Auto-resolve git conflict markers by keeping the stashed/local side.

This script is a conservative repo-wide resolver. It creates backups with the
suffix '.bak-conflict-resolve' before rewriting files. It keeps the text
between '=======' and '>>>>>>>' (the stashed/local/ours side) for each
conflict block.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".git", ".venv", "build", "dist", "node_modules", "__pycache__"}


def _split_conflict_blocks(text: str) -> tuple[bool, str]:
    """Return (changed, new_text). If a malformed conflict is found,
    returns (False, original_text) to avoid partial edits.
    """
    parts: list[str] = []
    i = 0
    changed = False
    while True:
        s = text.find("<<<<<<<", i)
        if s == -1:
            parts.append(text[i:])
            break
        changed = True
        parts.append(text[i:s])
        e = text.find("=======", s)
        if e == -1:
            return False, text
        g = text.find(">>>>>>>", e)
        if g == -1:
            return False, text
        # Find the start of the line containing '>>>>>>>'
        line_start = text.rfind("\n", 0, g)
        if line_start == -1:
            line_start = 0
        else:
            line_start += 1  # move past the newline
        # keep the section between '=======' and the '>>>>>>>' line (stashed/local side)
        stashed = text[e + len("=======") : line_start]
        # Remove leading newline if present (from the ======= line)
        if stashed.startswith("\n"):
            stashed = stashed[1:]
        # Remove trailing newline if present (before >>>>>>> line)
        if stashed.endswith("\n"):
            stashed = stashed[:-1]
        parts.append(stashed + "\n")
        i = text.find("\n", g)
        if i == -1:
            i = len(text)
        else:
            i += 1  # move past the newline
    return changed, "".join(parts)


def resolve_file(path: Path) -> bool:
    try:
        txt = path.read_text(encoding="utf-8")
    except Exception:
        # unreadable (binary/permission) -> skip
        return False
    changed, new = _split_conflict_blocks(txt)
    if not changed:
        return True
    bak = path.with_suffix(path.suffix + ".bak-conflict-resolve")
    bak.write_text(txt, encoding="utf-8")
    path.write_text(new, encoding="utf-8")
    return True


def main() -> int:
    modified = []
    failed = []
    for p in ROOT.rglob("*"):
        if p.is_dir():
            continue
        if set(p.parts) & EXCLUDE:
            continue
        ok = resolve_file(p)
        if ok:
            bak = p.with_suffix(p.suffix + ".bak-conflict-resolve")
            if bak.exists():
                modified.append(str(p))
        else:
            failed.append(str(p))
    print("Conflict resolution run summary:")
    print(f"  Files modified: {len(modified)}")
    for m in modified:
        print("   -", m)
    if failed:
        print(f"\n  Files failed: {len(failed)}")
        for f in failed:
            print("   -", f)
        return 2
    print("\nAll done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
