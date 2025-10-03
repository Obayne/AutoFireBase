from PySide6 import QtCore, QtWidgets


def _nearest_line_item(scene: QtWidgets.QGraphicsScene, p: QtCore.QPointF):
    box = QtCore.QRectF(p.x() - 4, p.y() - 4, 8, 8)
    for it in scene.items(box):
        if isinstance(it, QtWidgets.QGraphicsLineItem):
            return it
    return None


class ChamferTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.first = None
        self.d1 = 1.0
        self.d2 = 1.0

    def start(self):
        self.active = True
        self.first = None
        dlg = QtWidgets.QDialog(self.win)
        dlg.setWindowTitle("Chamfer")
        form = QtWidgets.QFormLayout(dlg)
        s1 = QtWidgets.QDoubleSpinBox()
        s1.setRange(0, 1000)
        s1.setDecimals(2)
        s1.setValue(1.0)
        s2 = QtWidgets.QDoubleSpinBox()
        s2.setRange(0, 1000)
        s2.setDecimals(2)
        s2.setValue(1.0)
        form.addRow("Distance 1 (ft):", s1)
        form.addRow("Distance 2 (ft):", s2)
        bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        form.addRow(bb)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        if dlg.exec() == QtWidgets.QDialog.Accepted:
            self.d1 = float(s1.value())
            self.d2 = float(s2.value())
            self.win.statusBar().showMessage("Chamfer: click first line, then second")
        else:
            self.active = False

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
            return False
        if self.first is None:
            self.first = it
            return False
        if it is self.first:
            return False
        # Trim both lines back by distances along each from the intersection point
        l1 = QtCore.QLineF(self.first.line())
        l2 = QtCore.QLineF(it.line())
        ip = QtCore.QPointF()
        inter = l1.intersect(l2, ip)
        if inter == QtCore.QLineF.NoIntersection:
            self.active = False
            self.first = None
            return False

        def move_line(line: QtCore.QLineF, dist_ft: float, px_per_ft: float):
            a = QtCore.QPointF(line.x1(), line.y1())
            b = QtCore.QPointF(line.x2(), line.y2())
            da = QtCore.QLineF(a, ip).length()
            db = QtCore.QLineF(b, ip).length()
            dpx = dist_ft * px_per_ft
            if da < db:
                v = QtCore.QLineF(ip, a)
                ln = v.length() or 1.0
                ux = (a.x() - ip.x()) / ln
                uy = (a.y() - ip.y()) / ln
                a = QtCore.QPointF(ip.x() + ux * dpx, ip.y() + uy * dpx)
            else:
                v = QtCore.QLineF(ip, b)
                ln = v.length() or 1.0
                ux = (b.x() - ip.x()) / ln
                uy = (b.y() - ip.y()) / ln
                b = QtCore.QPointF(ip.x() + ux * dpx, ip.y() + uy * dpx)
            return QtCore.QLineF(a, b)

        nl1 = move_line(l1, self.d1, self.win.px_per_ft)
        nl2 = move_line(l2, self.d2, self.win.px_per_ft)
        self.first.setLine(nl1)
        it.setLine(nl2)
        self.active = False
        self.first = None
        return True
