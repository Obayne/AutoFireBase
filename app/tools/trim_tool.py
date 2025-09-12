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
    # Compute intersection of infinite lines using vector math
    x1, y1, x2, y2 = l1.x1(), l1.y1(), l1.x2(), l1.y2()
    x3, y3, x4, y4 = l2.x1(), l2.y1(), l2.x2(), l2.y2()
    den = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / den
    py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / den
    return QtCore.QPointF(px, py)


class TrimTool:
    """Simple trim: pick cutting line, then target line; trims target to intersection near pick.

    Limitations: operates on QGraphicsLineItem only.
    """

    def __init__(self, window):
        self.win = window
        self.active = False
        self.cut_item = None

    def start(self):
        self.active = True
        self.cut_item = None
        self.win.statusBar().showMessage("Trim: click cutting line, then target line to trim")

    def cancel(self):
        self.active = False
        self.cut_item = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        sc = self.win.scene
        it = _nearest_line_item(sc, p)
        if it is None:
            self.win.statusBar().showMessage("Trim: no line here")
            return False
        if self.cut_item is None:
            self.cut_item = it
            self.win.statusBar().showMessage("Trim: now click target line to trim")
            return False
        # Trim target to intersection with cut
        if it is self.cut_item:
            self.win.statusBar().showMessage("Trim: pick a different target line")
            return False
        lcut = _line_from_item(self.cut_item)
        ltar = _line_from_item(it)
        ip = _intersection_point(lcut, ltar)
        if ip is None:
            self.win.statusBar().showMessage("Trim: lines do not intersect")
            self.active = False
            self.cut_item = None
            return False
        # pick closer endpoint to the click point
        d1 = QtCore.QLineF(p, QtCore.QPointF(ltar.x1(), ltar.y1())).length()
        d2 = QtCore.QLineF(p, QtCore.QPointF(ltar.x2(), ltar.y2())).length()
        if d1 < d2:
            it.setLine(ip.x(), ip.y(), ltar.x2(), ltar.y2())
        else:
            it.setLine(ltar.x1(), ltar.y1(), ip.x(), ip.y())
        self.win.statusBar().showMessage("Trimmed")
        self.active = False
        self.cut_item = None
        return True

