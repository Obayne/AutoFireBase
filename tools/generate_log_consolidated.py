"""Generate a consolidated log summary for developer review.

Scans common log files and CI artifacts and writes `docs/LOG_CONSOLIDATED.md`.

This is intentionally small and safe to run locally.
"""

import logging
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "LOG_CONSOLIDATED.md"
LOG_LOCATIONS = [
    ROOT / "quick-tests-18146321953.tail.log",
    ROOT / "ci" / "global_tasklist.yml",
    ROOT / "tools" / "run_app_debug.py",
    ROOT / "updater" / "updater.log",
]


def scan_files():
    hits = []
    for p in LOG_LOCATIONS:
        if not p.exists():
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError) as e:
            hits.append((str(p), f"Failed to read: {e}"))
            continue
        # find error/traceback lines and a few context lines
        for m in re.finditer(r"(?im)^(.*error.*|traceback|internalerror).*", text):
            line = m.group(0).strip()
            hits.append((str(p.relative_to(ROOT)), line))
    return hits


def write_md(hits):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# Consolidated Log Summary\n\n")
        if not hits:
            f.write("No notable errors or traces found in scanned locations.\n")
            return
        f.write("Found log items from the following files:\n\n")
        for path, line in hits:
            f.write(f"- `{path}`: {line}\n")
    logging.getLogger(__name__).info("Wrote %s", OUT)


def main():
    hits = scan_files()
    write_md(hits)
    # logging configured by caller; emit info if not
    logging.getLogger(__name__).info("Consolidated log summary generated")


if __name__ == "__main__":
    main()
