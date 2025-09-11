from PySide6 import QtCore, QtGui, QtWidgets
from app.device import DeviceItem
from app import units

class ArrayDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Array Placement")
        f = QtWidgets.QFormLayout(self)
        self.spacing_x = QtWidgets.QDoubleSpinBox(); self.spacing_x.setRange(0.1, 500); self.spacing_x.setValue(15.0); self.spacing_x.setSuffix(" ft")
        self.spacing_y = QtWidgets.QDoubleSpinBox(); self.spacing_y.setRange(0.1, 500); self.spacing_y.setValue(15.0); self.spacing_y.setSuffix(" ft")
        f.addRow("Spacing X:", self.spacing_x)
        f.addRow("Spacing Y:", self.spacing_y)
        bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        f.addRow(bb)

    def get(self):
        return float(self.spacing_x.value()), float(self.spacing_y.value())

class ArrayTool:
    def __init__(self, window, layer_devices):
        self.win = window
        self.layer = layer_devices
        self.pending = False
        self.p0 = None
        self.spacing_ft = (15.0, 15.0)

    def run(self):
        dlg = ArrayDialog(self.win)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        self.spacing_ft = dlg.get()
        self.win.statusBar().showMessage("Array: click first corner, then opposite corner")
        self.pending = True
        self.p0 = None

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.pending: return False
        if self.p0 is None:
            self.p0 = p; return False
        # place array within rect p0..p
        r = QtCore.QRectF(self.p0, p).normalized()
        sx_ft, sy_ft = self.spacing_ft
        pxft = self.win.px_per_ft
        sx_px = sx_ft * pxft; sy_px = sy_ft * pxft
        proto = self.win.current_proto or {"symbol":"SD","name":"Smoke Detector","manufacturer":"(Any)","part_number":"GEN-SD"}
        y = r.top() + sy_px/2
        placed = 0
        while y < r.bottom():
            x = r.left() + sx_px/2
            while x < r.right():
                it = DeviceItem(x, y, proto["symbol"], proto["name"], proto.get("manufacturer",""), proto.get("part_number",""))
                it.setParentItem(self.layer)
                placed += 1
                x += sx_px
            y += sy_px
        self.win.push_history()
        self.win.statusBar().showMessage(f"Array placed: {placed} devices")
        self.pending = False
        self.p0 = None
        return True
