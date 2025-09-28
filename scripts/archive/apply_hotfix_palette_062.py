# apply_hotfix_palette_062.py
# Fix QPalette usage: replace pal.setColor(pal.X, ...) -> pal.setColor(QtGui.QPalette.X, ...)
import time
from pathlib import Path

root = Path(".").resolve()
target = root / "app" / "main.py"
stamp = time.strftime("%Y%m%d_%H%M%S")

if not target.exists():
    raise SystemExit(f"Not found: {target}")

src = target.read_text(encoding="utf-8")
bak = target.with_suffix(target.suffix + f".bak-{stamp}")
bak.write_text(src, encoding="utf-8")

# Replace any 'pal.setColor(pal.' with 'pal.setColor(QtGui.QPalette.'
fixed = src.replace("pal.setColor(pal.", "pal.setColor(QtGui.QPalette.")

# Also handle lines that might use ColorRole API partially/mixed later (noop if not present)
fixed = fixed.replace("QtGui.QPalette.ColorRole.", "QtGui.QPalette.")

target.write_text(fixed, encoding="utf-8")
print(f"Backed up to: {bak}")
print(f"Patched:      {target}")
