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


class FilletTool:
    """Zero-radius fillet (corner): trims/extends two lines so they meet at intersection.

    Note: This implements fillet with radius=0 for speed. Radius arcs can be
    added later.
    """
    def __init__(self, window):
        self.win = window
        self.active = False
        self.first = None

    def start(self):
        self.active = True
        self.first = None
        self.win.statusBar().showMessage("Fillet: click first line, then second line")

    def cancel(self):
        self.active = False
        self.first = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        sc = self.win.scene
        it = _nearest_line_item(sc, p)
        if it is None:
            self.win.statusBar().showMessage("Fillet: no line here")
            return False
        if self.first is None:
            self.first = it
            self.win.statusBar().showMessage("Fillet: now click the second line")
            return False
        if it is self.first:
            self.win.statusBar().showMessage("Fillet: pick a different second line")
            return False
        l1 = _line_from_item(self.first)
        l2 = _line_from_item(it)
        ip = _intersection_point(l1, l2)
        if ip is None:
            self.win.statusBar().showMessage("Fillet: lines do not intersect")
            self.active = False; self.first = None
            return False
        # Trim/extend both to intersection
        it1 = self.first; it2 = it
        # choose closer endpoints to move for both lines
        for (li, item) in ((l1, it1), (l2, it2)):
            d1 = QtCore.QLineF(ip, QtCore.QPointF(li.x1(), li.y1())).length()
            d2 = QtCore.QLineF(ip, QtCore.QPointF(li.x2(), li.y2())).length()
            if d1 < d2:
                item.setLine(ip.x(), ip.y(), li.x2(), li.y2())
            else:
                item.setLine(li.x1(), li.y1(), ip.x(), ip.y())
        self.active = False; self.first = None
        self.win.statusBar().showMessage("Fillet (corner) applied")
        return True

