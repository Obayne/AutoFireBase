# apply_arrayfix.py  — writes app/tools/array.py and hardens main.py import
from pathlib import Path
import re, datetime

ROOT = Path(".")
ARR = ROOT / "app" / "tools" / "array.py"
MAIN = ROOT / "app" / "main.py"

ARRAY_CODE = """from dataclasses import dataclass
from PySide6 import QtCore

@dataclass
class ArraySpec:
    spacing_ft: float = 10.0
    offset_ft_x: float = 0.0
    offset_ft_y: float = 0.0

def fill_rect_with_points(rect_px: QtCore.QRectF, px_per_ft: float, spec: ArraySpec):
    # Return list of QPointF inside rect at a regular grid spacing.
    if rect_px.width() <= 0 or rect_px.height() <= 0 or px_per_ft <= 0:
        return []
    step = spec.spacing_ft * px_per_ft
    ox = rect_px.left() + spec.offset_ft_x * px_per_ft
    oy = rect_px.top()  + spec.offset_ft_y * px_per_ft
    pts = []
    y = oy
    while y <= rect_px.bottom() - 1e-6:
        x = ox
        while x <= rect_px.right() - 1e-6:
            pts.append(QtCore.QPointF(x, y))
            x += step
        y += step
    return pts
"""

SAFE_IMPORT_BLOCK = """# SAFE import: array helpers (never crash on missing module)
try:
    from app.tools.array import ArraySpec, fill_rect_with_points  # type: ignore
except Exception:
    from dataclasses import dataclass
    from PySide6 import QtCore
    @dataclass
    class ArraySpec:
        spacing_ft: float = 10.0
        offset_ft_x: float = 0.0
        offset_ft_y: float = 0.0
    def fill_rect_with_points(rect_px: QtCore.QRectF, px_per_ft: float, spec: 'ArraySpec'):
        if rect_px.width() <= 0 or rect_px.height() <= 0 or px_per_ft <= 0:
            return []
        step = spec.spacing_ft * px_per_ft
        ox = rect_px.left() + spec.offset_ft_x * px_per_ft
        oy = rect_px.top()  + spec.offset_ft_y * px_per_ft
        pts = []
        y = oy
        while y <= rect_px.bottom() - 1e-6:
            x = ox
            while x <= rect_px.right() - 1e-6:
                pts.append(QtCore.QPointF(x, y))
                x += step
            y += step
        return pts
"""

def backup(p: Path):
    if p.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        p.with_suffix(p.suffix + f".bak_{ts}").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

# 1) Ensure app/tools/array.py exists with ArraySpec
ARR.parent.mkdir(parents=True, exist_ok=True)
backup(ARR)
ARR.write_text(ARRAY_CODE, encoding="utf-8")
print("wrote", ARR)

# 2) Harden main.py import (replace plain 'from app.tools.array import ...' with SAFE_IMPORT_BLOCK)
if MAIN.exists():
    txt = MAIN.read_text(encoding="utf-8")
    pattern = r"from\\s+app\\.tools\\.array\\s+import[\\s\\S]*?\\n"
    if re.search(pattern, txt):
        backup(MAIN)
        txt = re.sub(pattern, SAFE_IMPORT_BLOCK + "\n", txt, count=1)
        MAIN.write_text(txt, encoding="utf-8")
        print("patched", MAIN, "(safe import)")
    else:
        # If no plain import found, ensure the SAFE block exists once after other imports
        if "SAFE import: array helpers" not in txt:
            backup(MAIN)
            # insert after the last 'from app.' or 'import' block near top
            lines = txt.splitlines()
            insert_at = 0
            for i, line in enumerate(lines[:200]):
                if line.strip().startswith(("from ", "import ")):
                    insert_at = i + 1
            lines.insert(insert_at, SAFE_IMPORT_BLOCK)
            MAIN.write_text("\\n".join(lines), encoding="utf-8")
            print("inserted safe import block into", MAIN)
else:
    print("WARNING: app/main.py not found — only array.py was created.")
print("Done.")
