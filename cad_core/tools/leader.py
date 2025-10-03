from PySide6 import QtCore, QtGui, QtWidgets


class LeaderTool:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False
        self.p0 = None
        self.p1 = None

    def start(self):
        self.active = True
        self.p0 = None
        self.p1 = None
        self.win.statusBar().showMessage("Leader: click arrow point, then text point")

    def cancel(self):
        self.active = False
        self.p0 = None
        self.p1 = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.p0 is None:
            self.p0 = QtCore.QPointF(p)
            return False
        self.p1 = QtCore.QPointF(p)
        txt, ok = QtWidgets.QInputDialog.getText(self.win, "Leader Text", "Text:")
        if not ok:
            self.active = False
            return False
        # line
        line = QtWidgets.QGraphicsLineItem(self.p0.x(), self.p0.y(), self.p1.x(), self.p1.y())
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0"))
        pen.setCosmetic(True)
        line.setPen(pen)
        line.setZValue(20)
        line.setParentItem(self.layer)
        line.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        line.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        # arrow head
        v = QtCore.QLineF(self.p1, self.p0)
        v.setLength(12)
        left = v.normalVector()
        left.setLength(6)
        right = v.normalVector()
        right.setLength(-6)
        p2 = v.p2()
        lpt = QtCore.QPointF(p2.x() + left.dx(), p2.y() + left.dy())
        rpt = QtCore.QPointF(p2.x() + right.dx(), p2.y() + right.dy())
        poly = QtGui.QPolygonF([self.p0, lpt, rpt])
        head = QtWidgets.QGraphicsPolygonItem(poly)
        head.setBrush(QtGui.QColor("#e0e0e0"))
        head.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        head.setZValue(20)
        head.setParentItem(self.layer)
        # text
        t = QtWidgets.QGraphicsSimpleTextItem(txt)
        t.setBrush(QtGui.QBrush(QtGui.QColor("#e0e0e0")))
        t.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        t.setPos(self.p1 + QtCore.QPointF(8, -8))
        t.setParentItem(self.layer)
        t.setZValue(20)
        self.active = False
        return True
