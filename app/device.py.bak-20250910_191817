
from PySide6 import QtCore, QtGui, QtWidgets

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, x: float, y: float, symbol: str, name: str, manufacturer: str = "", part_number: str = ""):
        super().__init__()
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.locked = False  # NEW

        # Label offset (CAD-friendly)
        self.label_offset = QtCore.QPointF(12, -14)

        # Base glyph
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        pen = QtGui.QPen(Qt.black); pen.setCosmetic(True)
        self._glyph.setPen(pen)
        self._glyph.setBrush(QtGui.QBrush(Qt.white))
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(self.label_offset)
        self.addToGroup(self._label)

        # Coverage overlay
        self.coverage = {"mode":"none","mount":"ceiling","radius_ft":0.0,"px_per_ft":12.0,
                         "speaker":{"model":"physics (20log)","db_ref":95.0,"target_db":75.0,"loss10":6.0},
                         "strobe":{"candela":177.0,"target_lux":0.2},
                         "computed_radius_px": 0.0}
        self._cov_circle = None
        self._cov_square = None   # for ceiling strobe: circle inside square
        self._cov_rect = None     # for wall: rectangle (simplified)

        self.setPos(x, y)

    # ---------- lock / unlock ----------
    def set_locked(self, v: bool):
        self.locked = bool(v)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, not self.locked)
        # keep selectable so context menu can unlock later

        # subtle visual hint when locked
        pen = self._glyph.pen()
        pen.setStyle(QtCore.Qt.SolidLine if not self.locked else QtCore.Qt.DotLine)
        self._glyph.setPen(pen)

    def is_locked(self) -> bool:
        return bool(self.locked)

    # ---------- labels ----------
    def set_label_text(self, text: str):
        self._label.setText(text)

    def set_label_offset(self, dx: float, dy: float):
        self.label_offset = QtCore.QPointF(dx, dy)
        self._label.setPos(self.label_offset)

    # -------- coverage drawing ----------
    def set_coverage(self, settings: dict):
        if not settings: return
        self.coverage.update(settings)
        self._update_coverage_items()

    def _ensure_cov_items(self):
        if self._cov_circle is None:
            self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setParentItem(self); self._cov_circle.setZValue(-5)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,200)); pen.setStyle(QtCore.Qt.DashLine); pen.setCosmetic(True)
            self._cov_circle.setPen(pen); self._cov_circle.setBrush(QtGui.QColor(50,120,255,60))
        if self._cov_square is None:
            self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setParentItem(self); self._cov_square.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(QtCore.Qt.DotLine); pen.setCosmetic(True)
            self._cov_square.setPen(pen); self._cov_square.setBrush(QtGui.QColor(50,120,255,30))
        if self._cov_rect is None:
            self._cov_rect = QtWidgets.QGraphicsRectItem(); self._cov_rect.setParentItem(self); self._cov_rect.setZValue(-6)
            pen = QtGui.QPen(QtGui.QColor(50,120,255,120)); pen.setStyle(QtCore.Qt.DotLine); pen.setCosmetic(True)
            self._cov_rect.setPen(pen); self._cov_rect.setBrush(QtGui.QColor(50,120,255,30))

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        mount = self.coverage.get("mount","ceiling")
        r_px = float(self.coverage.get("computed_radius_px") or 0.0)

        # Hide all first
        for it in (self._cov_circle, self._cov_square, self._cov_rect):
            if it: it.setVisible(False)

        if mode=="none" or r_px <= 0:
            return

        self._ensure_cov_items()
        # Always draw circle
        self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px); self._cov_circle.setVisible(True)

        if mount=="ceiling" and mode=="strobe":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side); self._cov_square.setVisible(True)
        elif mount=="wall" and mode in ("strobe","speaker"):
            self._cov_rect.setRect(0, -r_px, r_px*2.0, r_px*2.0); self._cov_rect.setVisible(True)

    # -------- serialization ----------
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
            "locked": bool(self.locked),
            "z": float(self.zValue()),
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        d.get("symbol","?"), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""))
        off = d.get("label_offset")
        if isinstance(off,(list,tuple)) and len(off)==2:
            it.set_label_offset(float(off[0]), float(off[1]))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        it.set_locked(bool(d.get("locked", False)))
        if "z" in d:
            try: it.setZValue(float(d.get("z", 0)))
            except Exception: pass
        return it
