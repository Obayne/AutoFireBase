from PySide6 import QtCore, QtGui, QtWidgets


class TextTool:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False

    def start(self):
        self.active = True
        self.win.statusBar().showMessage(
            "Text: click to place, then enter text (use MText for scalable)"
        )

    def cancel(self):
        self.active = False

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        txt, ok = QtWidgets.QInputDialog.getText(self.win, "Insert Text", "Text:")
        if not ok or not txt:
            self.active = False
            return False
        it = QtWidgets.QGraphicsSimpleTextItem(txt)
        it.setPos(p)
        it.setBrush(QtGui.QBrush(QtGui.QColor("#e0e0e0")))
        it.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        it.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        it.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        it.setParentItem(self.layer)
        self.active = False
        self.win.statusBar().showMessage("Text placed")
        return True


class MTextTool:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.active = False
        self.text = ""
        self.height_ft = 1.0

    def start(self):
        self.active = True
        dlg = QtWidgets.QDialog(self.win)
        dlg.setWindowTitle("MText")
        form = QtWidgets.QFormLayout(dlg)
        txt = QtWidgets.QTextEdit()
        txt.setPlainText("")
        h = QtWidgets.QDoubleSpinBox()
        h.setRange(0.1, 100.0)
        h.setDecimals(2)
        h.setValue(1.0)
        form.addRow("Text:", txt)
        form.addRow("Height (ft):", h)
        bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        form.addRow(bb)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            self.active = False
            return
        self.text = txt.toPlainText()
        self.height_ft = float(h.value())
        self.win.statusBar().showMessage("MText: click to place")

    def cancel(self):
        self.active = False

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if not self.text:
            self.active = False
            return False
        item = QtWidgets.QGraphicsTextItem(self.text)
        item.setDefaultTextColor(QtGui.QColor("#e0e0e0"))
        item.setPos(p)
        # scale to desired height in pixels
        desired_px = float(self.height_ft) * float(self.win.px_per_ft)
        br = item.boundingRect()
        if br.height() > 0:
            s = desired_px / br.height()
            item.setScale(s)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        item.setParentItem(self.layer)
        self.active = False
        self.win.statusBar().showMessage("MText placed")
        return True
