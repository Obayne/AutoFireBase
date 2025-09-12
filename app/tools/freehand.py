from PySide6 import QtCore, QtGui, QtWidgets


class FreehandTool:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False
        self.drawing = False
        self.path_item = None
        self.last_pt = None

    def start(self):
        self.active = True
        self.drawing = False
        self.path_item = None
        self.last_pt = None
        self.win.statusBar().showMessage("Freehand: press and drag to draw, release to finish")

    def cancel(self):
        self.active = False
        if self.path_item and self.path_item.scene():
            try: self.path_item.scene().removeItem(self.path_item)
            except Exception: pass
        self.path_item = None
        self.last_pt = None
        self.drawing = False

    def on_press(self, p: QtCore.QPointF):
        if not self.active:
            return False
        self.drawing = True
        self.last_pt = QtCore.QPointF(p)
        path = QtGui.QPainterPath(p)
        self.path_item = QtWidgets.QGraphicsPathItem(path)
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
        self.path_item.setPen(pen); self.path_item.setZValue(20); self.path_item.setParentItem(self.layer)
        return False

    def on_mouse_move(self, p: QtCore.QPointF):
        if not (self.active and self.drawing and self.path_item):
            return
        if self.last_pt is None:
            self.last_pt = QtCore.QPointF(p)
        if QtCore.QLineF(self.last_pt, p).length() < 2.0:
            return
        path = QtGui.QPainterPath(self.path_item.path())
        path.lineTo(p)
        self.path_item.setPath(path)
        self.last_pt = QtCore.QPointF(p)

    def on_release(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if not self.drawing:
            return False
        self.drawing = False
        if self.path_item:
            self.path_item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
            self.path_item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.active = False
        self.win.statusBar().showMessage("Freehand path created")
        return True

