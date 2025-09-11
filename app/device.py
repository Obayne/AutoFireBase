from PySide6 import QtCore, QtGui, QtWidgets

class DeviceItem(QtWidgets.QGraphicsItemGroup):
    """Device glyph + label + optional coverage overlays (strobe/speaker/smoke)."""
    Type = QtWidgets.QGraphicsItem.UserType + 101

    def type(self): return DeviceItem.Type

    def __init__(self, x, y, symbol, name, manufacturer="", part_number=""):
        super().__init__()
        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsMovable |
            QtWidgets.QGraphicsItem.ItemIsSelectable
        )
        self.symbol = symbol
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number

        # Base glyph
        self._glyph = QtWidgets.QGraphicsEllipseItem(-6, -6, 12, 12)
        pen = QtGui.QPen(QtGui.QColor("#D8D8D8")); pen.setCosmetic(True)
        self._glyph.setPen(pen); self._glyph.setBrush(QtGui.QColor("#20252B"))
        self.addToGroup(self._glyph)

        # Label
        self._label = QtWidgets.QGraphicsSimpleTextItem(self.name)
        self._label.setBrush(QtGui.QBrush(QtGui.QColor("#EAEAEA")))
        self._label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self._label.setPos(QtCore.QPointF(12, -14))
        self.addToGroup(self._label)

        # Selection halo
        self._halo = QtWidgets.QGraphicsEllipseItem(-9, -9, 18, 18)
        halo_pen = QtGui.QPen(QtGui.QColor(60,180,255,220)); halo_pen.setCosmetic(True); halo_pen.setWidthF(1.4)
        self._halo.setPen(halo_pen); self._halo.setBrush(QtCore.Qt.NoBrush)
        self._halo.setZValue(-1); self._halo.setVisible(False)
        self.addToGroup(self._halo)

        # Coverage overlays
        self.coverage = {"mode":"none", "mount":"ceiling",
                         "params":{},  # mode-specific inputs
                         "computed_radius_ft":0.0,
                         "px_per_ft":12.0}
        self._cov_circle = QtWidgets.QGraphicsEllipseItem(); self._cov_circle.setZValue(-10); self._cov_circle.setVisible(False)
        cpen = QtGui.QPen(QtGui.QColor(80,170,255,200)); cpen.setCosmetic(True); cpen.setStyle(QtCore.Qt.DashLine)
        self._cov_circle.setPen(cpen); self._cov_circle.setBrush(QtGui.QColor(80,170,255,40))
        self.addToGroup(self._cov_circle)

        self._cov_square = QtWidgets.QGraphicsRectItem(); self._cov_square.setZValue(-11); self._cov_square.setVisible(False)
        spen = QtGui.QPen(QtGui.QColor(80,170,255,140)); spen.setCosmetic(True); spen.setStyle(QtCore.Qt.DotLine)
        self._cov_square.setPen(spen); self._cov_square.setBrush(QtGui.QColor(80,170,255,25))
        self.addToGroup(self._cov_square)

        self.setPos(x, y)

    # ---- selection visual
    def itemChange(self, change, value):
        if change == QtWidgets.QGraphicsItem.ItemSelectedChange:
            sel = bool(value)
            self._halo.setVisible(sel)
        return super().itemChange(change, value)

    def set_label_text(self, text: str):
        self._label.setText(text)

    # ---- coverage API
    def set_coverage(self, cfg: dict):
        if not cfg: return
        self.coverage.update(cfg)
        self._update_coverage_items()

    def _update_coverage_items(self):
        mode = self.coverage.get("mode","none")
        r_ft = float(self.coverage.get("computed_radius_ft") or 0.0)
        ppf  = float(self.coverage.get("px_per_ft") or 12.0)
        r_px = r_ft * ppf

        # hide all
        self._cov_circle.setVisible(False)
        self._cov_square.setVisible(False)
        if mode == "none" or r_px <= 0:
            return

        # circle always
        self._cov_circle.setRect(-r_px, -r_px, 2*r_px, 2*r_px)
        self._cov_circle.setVisible(True)

        # if strobe + ceiling: show square footprint
        if mode == "strobe" and self.coverage.get("mount","ceiling") == "ceiling":
            side = 2*r_px
            self._cov_square.setRect(-side/2, -side/2, side, side)
            self._cov_square.setVisible(True)

    # ---- serialization
    def to_json(self):
        return {
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "symbol": self.symbol,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "part_number": self.part_number,
            "coverage": self.coverage,
        }

    @staticmethod
    def from_json(d: dict):
        it = DeviceItem(float(d.get("x",0)), float(d.get("y",0)),
                        d.get("symbol","?"), d.get("name","Device"),
                        d.get("manufacturer",""), d.get("part_number",""))
        cov = d.get("coverage")
        if cov: it.set_coverage(cov)
        return it
