from PySide6 import QtCore, QtGui


class MirrorTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.p1 = None
        self.p2 = None

    def start(self):
        self.active = True
        self.p1 = None
        self.p2 = None
        self.win.statusBar().showMessage("Mirror: click first point of axis, then second point")

    def cancel(self):
        self.active = False
        self.p1 = None
        self.p2 = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.p1 is None:
            self.p1 = p
            return False
        self.p2 = p
        sel = list(self.win.scene.selectedItems())
        if not sel:
            self.active = False
            self.p1 = None
            self.p2 = None
            return False
        # Build reflection transform about line p1-p2
        x1, y1 = self.p1.x(), self.p1.y()
        x2, y2 = self.p2.x(), self.p2.y()
        import math

        a = math.atan2(y2 - y1, x2 - x1)
        deg = a * 180.0 / math.pi
        t = QtGui.QTransform()
        t.translate(x1, y1)
        t.rotate(deg)
        t.scale(1, -1)
        t.rotate(-deg)
        t.translate(-x1, -y1)
        for it in sel:
            try:
                it.setTransform(t, combine=True)
            except Exception:
                pass
        self.active = False
        self.p1 = None
        self.p2 = None
        return True
