from PySide6 import QtCore, QtGui, QtWidgets

# Use CAD core for fillet computation
from cad_core.lines import Line as CoreLine, Point as CorePoint
from cad_core.fillet import fillet_segments_line_line
from frontend.qt_shapes import path_from_arc


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
    """Fillet two lines.

    Supports corner (radius=0) and radius > 0. Two clicks: first line then second.
    """
    def __init__(self, window):
        self.win = window
        self.active = False
        self.first = None
        self.first_pick = None

    def start(self):
        self.active = True
        self.first = None
        self.first_pick = None
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
            self.first_pick = QtCore.QPointF(p)
            self.win.statusBar().showMessage("Fillet: now click the second line")
            return False
        if it is self.first:
            self.win.statusBar().showMessage("Fillet: pick a different second line")
            return False
        # Ask for radius (default 0 for corner)
        radius, ok = QtWidgets.QInputDialog.getDouble(self.win, "Fillet radius", "Radius", 0.0, 0.0, 1e6, 2)
        l1 = _line_from_item(self.first)
        l2 = _line_from_item(it)
        if not ok or radius <= 0.0:
            # Corner mode: trim/extend both to their intersection
            ip = _intersection_point(l1, l2)
            if ip is None:
                self.win.statusBar().showMessage("Fillet: lines do not intersect")
                self.active = False; self.first = None; self.first_pick=None
                return False
            it1 = self.first; it2 = it
            for (li, item) in ((l1, it1), (l2, it2)):
                d1 = QtCore.QLineF(ip, QtCore.QPointF(li.x1(), li.y1())).length()
                d2 = QtCore.QLineF(ip, QtCore.QPointF(li.x2(), li.y2())).length()
                if d1 < d2:
                    item.setLine(ip.x(), ip.y(), li.x2(), li.y2())
                else:
                    item.setLine(li.x1(), li.y1(), ip.x(), ip.y())
            self.active = False; self.first = None; self.first_pick=None
            self.win.statusBar().showMessage("Fillet (corner) applied")
            return True

        # Radius mode using CAD core
        p1 = QtCore.QPointF(self.first_pick)
        p2 = QtCore.QPointF(p)
        seg1 = CoreLine(CorePoint(l1.x1(), l1.y1()), CorePoint(l1.x2(), l1.y2()))
        seg2 = CoreLine(CorePoint(l2.x1(), l2.y1()), CorePoint(l2.x2(), l2.y2()))
        out = fillet_segments_line_line(seg1, seg2, CorePoint(p1.x(), p1.y()), CorePoint(p2.x(), p2.y()), radius)
        if out is None:
            self.win.statusBar().showMessage("Fillet: cannot construct with given radius")
            self.active = False; self.first = None; self.first_pick=None
            return False
        ns1, ns2, arc = out
        # Update lines
        self.first.setLine(ns1.a.x, ns1.a.y, ns1.b.x, ns1.b.y)
        it.setLine(ns2.a.x, ns2.a.y, ns2.b.x, ns2.b.y)
        # Add arc path
        path = path_from_arc(arc)
        arc_item = QtWidgets.QGraphicsPathItem(path)
        pen = QtGui.QPen(QtGui.QColor('#ffa500'))
        pen.setCosmetic(True)
        arc_item.setPen(pen)
        it.scene().addItem(arc_item)
        self.active = False; self.first = None; self.first_pick=None
        self.win.statusBar().showMessage("Fillet (radius) applied")
        return True

