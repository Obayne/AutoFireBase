
from PySide6 import QtCore, QtGui, QtWidgets

PAGE_SIZES = {
    "Letter": (8.5, 11),
    "Tabloid": (11, 17),
    "A3": (11.69, 16.54),
    "A2": (16.54, 23.39),
    "A1": (23.39, 33.11),
    "A0": (33.11, 46.81),
}

class PageFrame(QtWidgets.QGraphicsItemGroup):
    def __init__(self, px_per_ft: float, size_name="Letter", orientation="Portrait", margin_in=0.5):
        super().__init__()
        self._px_per_ft = float(px_per_ft)
        self._size_name = size_name
        self._orient = orientation
        self._margin_in = float(margin_in)
        self._outer = QtWidgets.QGraphicsRectItem(); self._outer.setPen(QtGui.QPen(QtGui.QColor(180,180,180)))
        self._inner = QtWidgets.QGraphicsRectItem(); pen = QtGui.QPen(QtGui.QColor(130,130,130)); pen.setStyle(QtCore.Qt.DashLine); self._inner.setPen(pen)
        self.addToGroup(self._outer); self.addToGroup(self._inner)
        self.setZValue(-50)
        self._recalc()

    def _inch_to_px(self, inches: float) -> float:
        return (float(inches)/12.0) * self._px_per_ft

    def _recalc(self):
        w_in, h_in = PAGE_SIZES.get(self._size_name, PAGE_SIZES["Letter"])
        if (self._orient or "Portrait").lower().startswith("land"):
            w_in, h_in = h_in, w_in
        w_px = self._inch_to_px(w_in); h_px = self._inch_to_px(h_in)
        m = self._inch_to_px(self._margin_in)
        self._outer.setRect(0, 0, w_px, h_px)
        self._inner.setRect(m, m, max(0, w_px-2*m), max(0, h_px-2*m))

    def set_params(self, *, size_name=None, orientation=None, margin_in=None, px_per_ft=None):
        if size_name: self._size_name = size_name
        if orientation: self._orient = orientation
        if margin_in is not None: self._margin_in = float(margin_in)
        if px_per_ft is not None: self._px_per_ft = float(px_per_ft)
        self._recalc()
