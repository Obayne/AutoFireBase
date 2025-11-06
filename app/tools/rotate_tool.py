from PySide6 import QtCore, QtGui, QtWidgets


class RotateTool:
    def __init__(self, window):
        self.win = window
        self.active = False
        self.base = None

    def start(self):
        self.active = True
        self.base = None
        self.win.statusBar().showMessage("Rotate: click base point, then enter angle")

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
            # Prompt for angle degrees
            val, ok = QtWidgets.QInputDialog.getDouble(
                self.win, "Rotate", "Angle (deg)", 90.0, -360.0, 360.0, 2
            )
            if not ok:
                self.active = False
                self.base = None
                return False
            ang = float(val)
            _rad = ang * 3.141592653589793 / 180.0
            sel = list(self.win.scene.selectedItems())
            if not sel:
                self.active = False
                self.base = None
                return False
            cx, cy = self.base.x(), self.base.y()
            t = QtGui.QTransform()
            t.translate(cx, cy)
            t.rotate(ang)
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
