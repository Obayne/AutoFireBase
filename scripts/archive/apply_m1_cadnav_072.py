# apply_m1_cadnav_072.py
# M1: CAD feel – zoom-to-cursor, middle-mouse pan, major/minor grid.
# Safe: timestamped backups of app/main.py and app/scene.py

from pathlib import Path
import time, re

ROOT = Path(__file__).resolve().parent
STAMP = time.strftime("%Y%m%d_%H%M%S")
MAIN = ROOT / "app" / "main.py"
SCENE = ROOT / "app" / "scene.py"


def patch_main():
    if not MAIN.exists():
        print(f"[!] missing {MAIN}")
        return False
    src = MAIN.read_text(encoding="utf-8")
    bak = MAIN.with_suffix(".py.bak-" + STAMP)

    changed = False
    out = src

    # 1) CanvasView.__init__: ensure AnchorUnderMouse and flags for pan state
    if "class CanvasView" in out and "AnchorUnderMouse" not in out:
        out = re.sub(
            r"(class\s+CanvasView\([^)]+\):\s*def\s+__init__\([^)]*\):\s*super\(\).__init__\(scene\)\s*)",
            r"\1        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)\n"
            r"        self._space_panning = False\n"
            r"        self._mid_panning = False\n",
            out,
            flags=re.S,
        )
        changed = True

    # 2) wheelEvent: keep your scale but ensure smooth zoom; nothing to do if already present
    # (We assume you already scale; AnchorUnderMouse makes it "zoom to cursor")

    # 3) middle-mouse pan + spacebar pan (robust)
    if "def mousePressEvent(self, e: QtGui.QMouseEvent)" in out and "Qt.MiddleButton" not in out:
        out = re.sub(
            r"def mousePressEvent\(self, e: QtGui\.QMouseEvent\):\s*",
            (
                "def mousePressEvent(self, e: QtGui.QMouseEvent):\n"
                "        if e.button() == Qt.MiddleButton and not self._mid_panning:\n"
                "            self._mid_panning = True\n"
                "            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)\n"
                "            self.setCursor(Qt.OpenHandCursor)\n"
                "            # synthesize left-button press for ScrollHandDrag to engage\n"
                "            fake = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, e.position(), Qt.LeftButton, Qt.LeftButton, e.modifiers())\n"
                "            super().mousePressEvent(fake)\n"
                "            e.accept(); return\n"
            ),
            out,
        )
        changed = True

    if (
        "def mouseReleaseEvent(self, e: QtGui.QMouseEvent)" in out
        and "self._mid_panning" not in out
    ):
        out = re.sub(
            r"def mouseReleaseEvent\(self, e: QtGui\.QMouseEvent\):\s*",
            (
                "def mouseReleaseEvent(self, e: QtGui.QMouseEvent):\n"
                "        if self._mid_panning and e.button() == Qt.MiddleButton:\n"
                "            # synthesize left-button release to end ScrollHandDrag\n"
                "            fake = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease, e.position(), Qt.LeftButton, Qt.NoButton, e.modifiers())\n"
                "            super().mouseReleaseEvent(fake)\n"
                "            self._mid_panning = False\n"
                "            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)\n"
                "            self.setCursor(Qt.ArrowCursor)\n"
                "            e.accept(); return\n"
            ),
            out,
        )
        changed = True

    if "def keyPressEvent(self, e: QtGui.QKeyEvent)" in out and "Key_Space" not in out:
        out = re.sub(
            r"def keyPressEvent\(self, e: QtGui\.QKeyEvent\):\s*",
            (
                "def keyPressEvent(self, e: QtGui.QKeyEvent):\n"
                "        if e.key() == Qt.Key_Space and not self._space_panning:\n"
                "            self._space_panning = True\n"
                "            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)\n"
                "            self.setCursor(Qt.OpenHandCursor)\n"
                "            e.accept(); return\n"
            ),
            out,
        )
        changed = True

    if "def keyReleaseEvent(self, e: QtGui.QKeyEvent)" in out and "Key_Space" not in out:
        out = re.sub(
            r"def keyReleaseEvent\(self, e: QtGui\.QKeyEvent\):\s*",
            (
                "def keyReleaseEvent(self, e: QtGui.QKeyEvent):\n"
                "        if e.key() == Qt.Key_Space and self._space_panning:\n"
                "            self._space_panning = False\n"
                "            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)\n"
                "            self.setCursor(Qt.ArrowCursor)\n"
                "            e.accept(); return\n"
            ),
            out,
        )
        changed = True

    if changed:
        bak.write_text(src, encoding="utf-8")
        MAIN.write_text(out, encoding="utf-8")
        print(f"[backup] {bak}")
        print(f"[write ] {MAIN}")
    else:
        print("[ok] app/main.py already has CAD nav hooks or patterns not found.")
    return changed


def patch_scene():
    if not SCENE.exists():
        print(f"[!] missing {SCENE}")
        return False
    src = SCENE.read_text(encoding="utf-8")
    bak = SCENE.with_suffix(".py.bak-" + STAMP)

    # Replace/insert drawBackground with major/minor grid
    pattern = r"def\s+drawBackground\(\s*self,\s*painter,\s*rect\s*\):.*?(?=\n\s*def|\Z)"
    new_func = r"""
def drawBackground(self, painter, rect):
    # CAD-like grid: minor every grid_size, major every 5*grid_size
    from PySide6 import QtGui, QtCore
    g = float(self.grid_size)
    if g <= 0:
        return

    painter.save()
    painter.setRenderHint(QtGui.QPainter.Antialiasing, False)

    # Background brush (dark theme aware)
    bg = QtGui.QColor(28,28,30)
    painter.fillRect(rect, bg)

    left = int(rect.left()) - (int(rect.left()) % int(g))
    top  = int(rect.top())  - (int(rect.top())  % int(g))
    right = int(rect.right())
    bottom= int(rect.bottom())

    # Minor grid
    pen_minor = QtGui.QPen(QtGui.QColor(80,80,86,150))
    pen_minor.setCosmetic(True)
    painter.setPen(pen_minor)
    x = left
    while x <= right:
        painter.drawLine(x, top, x, bottom)
        x += g
    y = top
    while y <= bottom:
        painter.drawLine(left, y, right, y)
        y += g

    # Major grid (every 5)
    step = g * 5.0
    pen_major = QtGui.QPen(QtGui.QColor(110,110,120,170))
    pen_major.setCosmetic(True); pen_major.setWidthF(0.0)
    painter.setPen(pen_major)

    x = left - (left % int(step))
    if x < left: x += int(step)
    while x <= right:
        painter.drawLine(x, top, x, bottom)
        x += int(step)

    y = top - (top % int(step))
    if y < top: y += int(step)
    while y <= bottom:
        painter.drawLine(left, y, right, y)
        y += int(step)

    # Origin cross
    pen_origin = QtGui.QPen(QtGui.QColor(255,209,102,180))  # amber
    pen_origin.setCosmetic(True)
    painter.setPen(pen_origin)
    painter.drawLine(-10, 0, 10, 0)
    painter.drawLine(0, -10, 0, 10)

    painter.restore()
"""
    if re.search(pattern, src, flags=re.S):
        out = re.sub(pattern, new_func, src, flags=re.S)
    else:
        # try to append method inside class GridScene
        out = re.sub(
            r"(class\s+GridScene\([^)]+\):.*?)(\n\s*def\s+\w+\(self,.*)",
            r"\1\n" + new_func + r"\2",
            src,
            flags=re.S,
        )
        if out == src:
            # fallback: just append the func (assumes name matches, Python will use class method if indented; if not, user can compare)
            out = src + "\n\n" + new_func

    if out != src:
        bak.write_text(src, encoding="utf-8")
        SCENE.write_text(out, encoding="utf-8")
        print(f"[backup] {bak}")
        print(f"[write ] {SCENE}")
        return True
    else:
        print("[ok] app/scene.py grid already customized or pattern not found.")
        return False


if __name__ == "__main__":
    a = patch_main()
    b = patch_scene()
    print("\nDone. Launch with:  py -3 -m app.boot")
