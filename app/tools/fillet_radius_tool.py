from PySide6 import QtCore, QtGui, QtWidgets
import math


def _nearest_line(scene: QtWidgets.QGraphicsScene, p: QtCore.QPointF):
    box = QtCore.QRectF(p.x()-4, p.y()-4, 8, 8)
    for it in scene.items(box):
        if isinstance(it, QtWidgets.QGraphicsLineItem):
            return it
    return None


def _angle_between(l1: QtCore.QLineF, l2: QtCore.QLineF) -> float:
    a1 = math.atan2(l1.y2()-l1.y1(), l1.x2()-l1.x1())
    a2 = math.atan2(l2.y2()-l2.y1(), l2.x2()-l2.x1())
    d = abs(a2-a1)
    while d > math.pi: d -= 2*math.pi
    return abs(d)


def _line_unit(line: QtCore.QLineF) -> tuple[float, float]:
    dx = line.x2()-line.x1(); dy = line.y2()-line.y1()
    ln = math.hypot(dx, dy) or 1.0
    return dx/ln, dy/ln


class FilletRadiusTool:
    """Fillet with radius between two lines: trims lines and inserts arc tangent to both.

    Simplified: handles straight QGraphicsLineItem pairs that intersect at a point.
    """

    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False
        self.r_ft = 1.0
        self.first = None

    def start(self):
        dlg = QtWidgets.QInputDialog(self.win)
        dlg.setInputMode(QtWidgets.QInputDialog.DoubleInput)
        dlg.setLabelText("Radius (ft)")
        dlg.setDoubleDecimals(2)
        dlg.setDoubleRange(0.01, 1000.0)
        dlg.setDoubleValue(1.0)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            self.active = False; self.first=None
            return
        self.r_ft = float(dlg.doubleValue())
        self.active = True
        self.first = None
        self.win.statusBar().showMessage("Fillet(radius): click first line, then second line")

    def cancel(self):
        self.active = False
        self.first = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        sc = self.win.scene
        it = _nearest_line(sc, p)
        if it is None:
            return False
        if self.first is None:
            self.first = it
            return False
        if it is self.first:
            return False
        l1 = QtCore.QLineF(self.first.line())
        l2 = QtCore.QLineF(it.line())
        ip = QtCore.QPointF()
        if l1.intersect(l2, ip) != QtCore.QLineF.IntersectType.BoundedIntersection and l1.intersect(l2, ip) != QtCore.QLineF.IntersectType.UnboundedIntersection:
            self.active=False; self.first=None
            return False
        theta = _angle_between(l1, l2)
        if theta <= 1e-6 or theta >= math.pi-1e-6:
            self.active=False; self.first=None
            return False
        r_px = self.r_ft * float(self.win.px_per_ft)
        d = r_px * math.tan(theta/2.0)
        # Trim back along each line from ip by distance d
        def trim_point(line: QtCore.QLineF):
            a = QtCore.QPointF(line.x1(), line.y1()); b = QtCore.QPointF(line.x2(), line.y2())
            # choose endpoint closer to ip to retreat from ip along line direction
            da = QtCore.QLineF(ip, a).length(); db = QtCore.QLineF(ip, b).length()
            # unit vectors from ip towards endpoints
            if da <= db:
                dirl = QtCore.QLineF(ip, a)
                ux, uy = _line_unit(dirl)
                return QtCore.QPointF(ip.x()+ux*d, ip.y()+uy*d)
            else:
                dirl = QtCore.QLineF(ip, b)
                ux, uy = _line_unit(dirl)
                return QtCore.QPointF(ip.x()+ux*d, ip.y()+uy*d)
        p1 = trim_point(l1); p2 = trim_point(l2)
        # Update original lines to end at p1/p2 from their far endpoints
        def update_line(orig: QtWidgets.QGraphicsLineItem, line: QtCore.QLineF, trim_pt: QtCore.QPointF):
            a = QtCore.QPointF(line.x1(), line.y1()); b = QtCore.QPointF(line.x2(), line.y2())
            # keep far endpoint, set near endpoint to trim_pt
            if QtCore.QLineF(ip, a).length() <= QtCore.QLineF(ip, b).length():
                orig.setLine(trim_pt.x(), trim_pt.y(), b.x(), b.y())
            else:
                orig.setLine(a.x(), a.y(), trim_pt.x(), trim_pt.y())
        update_line(self.first, l1, p1); update_line(it, l2, p2)
        # Arc center calculation: bisector direction from corner
        # Compute unit directions from ip towards p1 and p2
        u1 = _line_unit(QtCore.QLineF(ip, p1))
        u2 = _line_unit(QtCore.QLineF(ip, p2))
        # Normalize bisector
        bx, by = (u1[0]+u2[0]), (u1[1]+u2[1])
        bl = math.hypot(bx, by) or 1.0
        bx /= bl; by /= bl
        # center is at distance r/sin(theta/2) from ip along bisector
        cc = r_px / math.sin(theta/2.0)
        cx = ip.x() + bx * cc
        cy = ip.y() + by * cc
        # Build arc between p1 and p2
        rect = QtCore.QRectF(cx - r_px, cy - r_px, 2*r_px, 2*r_px)
        start_ang = math.degrees(math.atan2(-(p1.y()-cy), (p1.x()-cx)))
        end_ang = math.degrees(math.atan2(-(p2.y()-cy), (p2.x()-cx)))
        sweep = end_ang - start_ang
        # normalize sweep to the smaller arc consistent with corner
        while sweep <= -180: sweep += 360
        while sweep > 180: sweep -= 360
        path = QtGui.QPainterPath()
        path.arcMoveTo(rect, start_ang)
        path.arcTo(rect, start_ang, sweep)
        arc_item = QtWidgets.QGraphicsPathItem(path)
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
        arc_item.setPen(pen); arc_item.setZValue(20); arc_item.setParentItem(self.layer)
        arc_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        arc_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.active=False; self.first=None
        return True

