from PySide6 import QtCore, QtGui, QtWidgets


class RevisionCloudTool:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False
        self.points = []
        self.temp = None

    def start(self):
        self.active = True
        self.points = []
        self.temp = None
        self.win.statusBar().showMessage("Rev Cloud: click to add points, Esc to finish")

    def cancel(self):
        if self.temp and self.temp.scene():
            try: self.temp.scene().removeItem(self.temp)
            except Exception: pass
        self.temp=None; self.points=[]; self.active=False

    def on_mouse_move(self, p: QtCore.QPointF):
        if not self.active or not self.points:
            return
        path = QtGui.QPainterPath(self.points[0])
        for pt in self.points[1:]:
            path.lineTo(pt)
        path.lineTo(p)
        if not self.temp:
            self.temp = QtWidgets.QGraphicsPathItem()
            pen = QtGui.QPen(QtGui.QColor("#ffaa00")); pen.setCosmetic(True); pen.setWidth(3)
            self.temp.setPen(pen); self.temp.setBrush(QtCore.Qt.NoBrush); self.temp.setParentItem(self.layer)
        self.temp.setPath(path)

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        self.points.append(QtCore.QPointF(p))
        return False

    def finish(self):
        if not self.points:
            self.cancel(); return False
        path = QtGui.QPainterPath(self.points[0])
        for pt in self.points[1:]:
            path.lineTo(pt)
        item = QtWidgets.QGraphicsPathItem(path)
        pen = QtGui.QPen(QtGui.QColor("#ffaa00")); pen.setCosmetic(True); pen.setWidth(3)
        item.setPen(pen); item.setBrush(QtCore.Qt.NoBrush); item.setParentItem(self.layer)
        item.setZValue(40)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        if self.temp and self.temp.scene():
            try: self.temp.scene().removeItem(self.temp)
            except Exception: pass
        self.temp=None; self.points=[]; self.active=False
        self.win.statusBar().showMessage("Revision cloud created")
        return True

