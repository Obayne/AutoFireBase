# apply_visuals_070.py
# Makes devices use distinct shapes/colors by "symbol" and improves theme contrast.
# Safe: backs up edited files with timestamp suffixes.

import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAMP = time.strftime("%Y%m%d_%H%M%S")

DEVICE_PY = ROOT / "app" / "device.py"
MAIN_PY = ROOT / "app" / "main.py"

DEVICE_PATCH = r"""
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x: float, y: float, symbol: str, name: str, manufacturer: str = "", part_number: str = ""):
        super().__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.symbol = (symbol or "").upper()
        self.name = name or "Device"
        self.manufacturer = manufacturer
        self.part_number = part_number

        # Label offset (CAD-friendly)
        self.label_offset = QtCore.QPointF(12, -14)

        # Visual style by symbol/name (simple heuristics; we can refine later)
        kind, color = self._classify(self.symbol, self.name)

        # Base glyph (12x12 logical)
        self._glyph = self._make_shape(kind, 12.0)
        pen = QtGui.QPen(Qt.black); pen.setCosmetic(True); pen.setWidthF(1.2)
        self._glyph.setPen(pen)
        self._glyph.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setBrush(QtGui.QBrush(Qt.white))
        self._label.setPos(self.label_offset)
        self.addToGroup(self._label)

        # Coverage overlay (kept from prior code; hidden by default)
        self.coverage = {"mode":"none","mount":"ceiling","radius_ft":0.0,"px_per_ft":12.0,
                         "speaker":{"model":"physics (20log)","db_ref":95.0,"target_db":75.0,"loss10":6.0},
                         "strobe":{"candela":177.0,"target_lux":0.2},
                         "computed_radius_px": 0.0}
        self._cov_circle = None
        self._cov_square = None
        self._cov_rect = None

        # A soft selection ring for visibility
        self._selring = QtWidgets.QGraphicsEllipseItem(-9, -9, 18, 18)
    sel_pen = QtGui.QPen(QtGui.QColor("#FFD166"))
    sel_pen.setCosmetic(True)
    sel_pen.setWidthF(2.0)
    sel_pen.setStyle(Qt.DashLine)
    self._selring.setPen(sel_pen)
        self._selring.setBrush(QtCore.Qt.NoBrush)
        self._selring.setZValue(-1)
        self._selring.setVisible(False)
        self.addToGroup(self._selring)

        self.setPos(x, y)

    # --- classification ---
    def _classify(self, sym: str, name: str):
        n = (name or "").upper()
        # colors: teal, amber, red, violet, aqua, gray
        if "SMOKE" in n or sym in ("S","SD","SM"):
            return ("circle", "#4cc9f0")
        if "HEAT" in n or sym in ("H","HD"):
            return ("triangle", "#ffbe0b")
        if "PULL" in n or sym in ("P","MP"):
            return ("square", "#e63946")
        if "HORN" in n or "SPEAKER" in n or sym in ("SPK","HN","BELL"):
            return ("diamond", "#9b5de5")
        if "STROBE" in n or sym in ("ST","HS"):
            return ("square", "#00f5d4")
        return ("circle", "#adb5bd")

    # --- shape factory ---
    def _make_shape(self, kind: str, size: float) -> QtWidgets.QGraphicsItem:
        s = size
        if kind == "circle":
            return QtWidgets.QGraphicsEllipseItem(-s/2, -s/2, s, s)
        if kind == "square":
            return QtWidgets.QGraphicsRectItem(-s/2, -s/2, s, s)
        if kind == "diamond":
            poly = QtGui.QPolygonF([
                QtCore.QPointF(0, -s/2),
                QtCore.QPointF(s/2, 0),
                QtCore.QPointF(0, s/2),
                QtCore.QPointF(-s/2, 0),
            ])
            item = QtWidgets.QGraphicsPolygonItem(poly)
            return item
        if kind == "triangle":
            h = (3**0.5)/2 * s
            poly = QtGui.QPolygonF([
                QtCore.QPointF(0, -h/2),
                QtCore.QPointF(s/2, h/2),
                QtCore.QPointF(-s/2, h/2),
            ])
            item = QtWidgets.QGraphicsPolygonItem(poly)
            return item
        return QtWidgets.QGraphicsEllipseItem(-s/2, -s/2, s, s)

    # --- selection feedback ---
    def itemChange(self, change, value):
        # Toggle selection ring visibility
        if change == QtWidgets.QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self._selring.setVisible(bool(self.isSelected()))
        return super().itemChange(change, value)

    def set_label_text(self, text: str):
        self._label.setText(text)

    def set_label_offset(self, dx: float, dy: float):
        self.label_offset = QtCore.QPointF(dx, dy)
        self._label.setPos(self.label_offset)

    # --- coverage (unchanged API) ---
    def set_coverage(self, settings: dict):
        if not settings: return
        self.coverage.update(settings)
        self._update_coverage_items()

    def _ensure_cov_items(self):
        if self._cov_circle is None:
            self._cov_circle = QtWidgets.QGraphicsEllipseItem()
            self._cov_circle.setParentItem(self)
            self._cov_circle.setZValue(-5)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,200))
            pen.setStyle(QtCore.Qt.DashLine)
            pen.setCosmetic(True)
            self._cov_circle.setPen(pen)
            self._cov_circle.setBrush(QtGui.QColor(50,120,255,40))
        if self._cov_square is None:
            self._cov_square = QtWidgets.QGraphicsRectItem()
            self._cov_square.setParentItem(self)
            self._cov_square.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120))
            pen.setStyle(QtCore.Qt.DotLine)
            pen.setCosmetic(True)
            self._cov_square.setPen(pen)
            self._cov_square.setBrush(QtGui.QColor(50,120,255,25))
        if self._cov_rect is None:
            self._cov_rect = QtWidgets.QGraphicsRectItem()
            self._cov_rect.setParentItem(self)
            self._cov_rect.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120))
            pen.setStyle(QtCore.Qt.DotLine)
            pen.setCosmetic(True)
            self._cov_rect.setPen(pen)
            self._cov_rect.setBrush(QtGui.QColor(50,120,255,25))

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        mount = self.coverage.get("mount","ceiling")
        r_px = float(self.coverage.get("computed_radius_px") or 0.0)
        for it in (self._cov_circle, self._cov_square, self._cov_rect):
            if it: it.setVisible(False)
        if mode=="none" or r_px <= 0:
            return
        self._ensure_cov_items()
    self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px)
    self._cov_circle.setVisible(True)
        if mount=="ceiling" and mode=="strobe":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side); self._cov_square.setVisible(True)
        elif mount=="wall" and mode in ("strobe","speaker"):
            self._cov_rect.setRect(0, -r_px, r_px*2.0, r_px*2.0); self._cov_rect.setVisible(True)

    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "label_offset": [self.label_offset.x(), self.label_offset.y()],
            "coverage": self.coverage,
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        (d.get("symbol","") or "").upper(), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""))
        off = d.get("label_offset")
        if isinstance(off,(list,tuple)) and len(off)==2:
            it.set_label_offset(float(off[0]), float(off[1]))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        return it
"""

THEMES_PATCH = r"""
THEMES = {
    "dark": {
        "window": (26,26,28), "base": (20,20,22), "text": (238,240,244),
        "button": (48,48,54), "button_text": (238,240,244),
        "bg_brush": (28,28,30)
    },
    "medium": {
        "window": (34,34,38), "base": (26,26,30), "text": (238,240,244),
        "button": (56,56,62), "button_text": (238,240,244),
        "bg_brush": (34,34,38)
    },
    "slate": {
        "window": (220,224,230), "base": (236,240,244), "text": (22,24,28),
        "button": (205,210,216), "button_text": (22,24,28),
        "bg_brush": (236,240,244)
    }
}
"""


def patch_device():
    if not DEVICE_PY.exists():
        print(f"[!] missing {DEVICE_PY}")
        return
    bak = DEVICE_PY.with_suffix(".py.bak-" + STAMP)
    bak.write_text(DEVICE_PY.read_text(encoding="utf-8"), encoding="utf-8")
    DEVICE_PY.write_text(DEVICE_PATCH.lstrip(), encoding="utf-8")
    print(f"[backup] {bak}")
    print(f"[write ] {DEVICE_PY}")


def patch_themes():
    if not MAIN_PY.exists():
        print(f"[!] missing {MAIN_PY}")
        return
    src = MAIN_PY.read_text(encoding="utf-8")
    if "THEMES =" not in src:
        print("[i] THEMES block not found; skipping theme patch.")
        return
    bak = MAIN_PY.with_suffix(".py.bak-" + STAMP)
    bak.write_text(src, encoding="utf-8")
    # Replace the THEMES dict (simple heuristic)
    start = src.find("THEMES =")
    end = src.find("\n}\n", start)
    if end != -1:
        end += 3
        new_src = src[:start] + THEMES_PATCH + src[end:]
    else:
        new_src = src + "\n\n" + THEMES_PATCH
    MAIN_PY.write_text(new_src, encoding="utf-8")
    print(f"[backup] {bak}")
    print(f"[write ] {MAIN_PY}")


if __name__ == "__main__":
    patch_device()
    patch_themes()
    print("\nDone. Restart with:  py -3 -m app.boot")
