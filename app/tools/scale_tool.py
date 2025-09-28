from PySide6 import QtCore, QtGui, QtWidgets


class ScaleTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.base = None

    def start(self):
        self.active = True
        self.base = None
        self.win.statusBar().showMessage("Scale: click base point, then enter factor")

    def cancel(self):
        self.active = False
        self.base = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.base is None:
            self.base = p
            val, ok = QtWidgets.QInputDialog.getDouble(
                self.win, "Scale", "Factor", 1.0, 0.01, 1000.0, 3
            )
            if not ok:
                self.active = False
                self.base = None
                return False
            f = float(val)
            sel = list(self.win.scene.selectedItems())
            if not sel:
                self.active = False
                self.base = None
                return False
            cx, cy = self.base.x(), self.base.y()
            t = QtGui.QTransform()
            t.translate(cx, cy)
            t.scale(f, f)
            t.translate(-cx, -cy)
            for it in sel:
                try:
                    it.setTransform(t, combine=True)
                except Exception:
                    pass
            self.active = False
            self.base = None
            return True
        return False
