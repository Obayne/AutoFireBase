# fix_device_qt_import_062.py
# Purpose: fix NameError in app/device.py by ensuring `from PySide6.QtCore import Qt`
# Safe: makes a timestamped backup alongside device.py

import sys
import time
from pathlib import Path

root = Path(__file__).resolve().parent
device_py = root / "app" / "device.py"


def main():
    if not device_py.exists():
        print(f"[error] Not found: {device_py}")
        sys.exit(1)

    src = device_py.read_text(encoding="utf-8", errors="ignore")
    if "from PySide6.QtCore import Qt" in src:
        print("[ok] device.py already imports Qt")
        return

    # Insert the Qt import just after the first PySide6 import block
    lines = src.splitlines()
    inserted = False
    for i, line in enumerate(lines):
        if line.strip().startswith("from PySide6") or line.strip().startswith("import PySide6"):
            # Look ahead to the end of the contiguous import block
            j = i
            while j + 1 < len(lines) and lines[j + 1].strip().startswith(
                ("from PySide6", "import PySide6")
            ):
                j += 1
            lines.insert(j + 1, "from PySide6.QtCore import Qt")
            inserted = True
            break

    if not inserted:
        # Fallback: add near the top
        lines.insert(0, "from PySide6.QtCore import Qt")

    new_src = "\n".join(lines)

    # backup + write
    stamp = time.strftime("%Y%m%d_%H%M%S")
    backup = device_py.with_suffix(".py.bak-" + stamp)
    backup.write_text(src, encoding="utf-8")
    device_py.write_text(new_src, encoding="utf-8")

    print(f"[backup] {backup}")
    print(f"[write ] {device_py}")
    print("Done. Launch with:  py -3 -m app.boot")


if __name__ == "__main__":
    main()
