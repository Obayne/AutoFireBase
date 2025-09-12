from PySide6 import QtCore, QtGui, QtWidgets


def _nearest_line_item(scene: QtWidgets.QGraphicsScene, p: QtCore.QPointF):
    box = QtCore.QRectF(p.x()-4, p.y()-4, 8, 8)
    for it in scene.items(box):
        if isinstance(it, QtWidgets.QGraphicsLineItem):
            return it
    return None


def _line_from_item(it: QtWidgets.QGraphicsLineItem) -> QtCore.QLineF:
    return QtCore.QLineF(it.line())


def _intersection_point(l1: QtCore.QLineF, l2: QtCore.QLineF):
    x1, y1, x2, y2 = l1.x1(), l1.y1(), l1.x2(), l1.y2()
    x3, y3, x4, y4 = l2.x1(), l2.y1(), l2.x2(), l2.y2()
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / den
    py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / den
    return QtCore.QPointF(px, py)


class ExtendTool:
    """Extend target line to meet boundary (cutting) line at intersection.

    Limitations: operates on QGraphicsLineItem only; extends the endpoint
    closest to the pick point.
    """
    def __init__(self, window):
        self.win = window
        self.active = False
        self.boundary = None

    def start(self):
        self.active = True
        self.boundary = None
        self.win.statusBar().showMessage("Extend: click boundary line, then target line to extend")

    def cancel(self):
        self.active = False
        self.boundary = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        sc = self.win.scene
        it = _nearest_line_item(sc, p)
        if it is None:
            self.win.statusBar().showMessage("Extend: no line here")
            return False
        if self.boundary is None:
            self.boundary = it
            self.win.statusBar().showMessage("Extend: now click target line to extend")
            return False
        if it is self.boundary:
            self.win.statusBar().showMessage("Extend: pick a different target line")
            return False
        lcut = _line_from_item(self.boundary)
        ltar = _line_from_item(it)
        ip = _intersection_point(lcut, ltar)
        if ip is None:
            self.win.statusBar().showMessage("Extend: lines do not intersect")
            self.active = False; self.boundary = None
            return False
        d1 = QtCore.QLineF(p, QtCore.QPointF(ltar.x1(), ltar.y1())).length()
        d2 = QtCore.QLineF(p, QtCore.QPointF(ltar.x2(), ltar.y2())).length()
        if d1 < d2:
            it.setLine(ip.x(), ip.y(), ltar.x2(), ltar.y2())
        else:
            it.setLine(ltar.x1(), ltar.y1(), ip.x(), ip.y())
        self.active = False; self.boundary = None
        self.win.statusBar().showMessage("Extended")
        return True

