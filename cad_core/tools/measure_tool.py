from PySide6 import QtCore, QtGui, QtWidgets


class MeasureTool:
    def __init__(self, window, overlay_layer):
        self.win = window
        self.layer = overlay_layer
        self.active = False
        self.start_pt = None
        self.temp = None

    def start(self):
        self.active = True
        self.start_pt = None
        self._clear()
        self.win.statusBar().showMessage("Measure: click first point, then second point")

    def cancel(self):
        self.active = False
        self._clear()

    def _clear(self):
        if self.temp and self.temp.scene():
            self.temp.scene().removeItem(self.temp)
        self.temp = None

    def on_mouse_move(self, p: QtCore.QPointF):
        if not self.active or self.start_pt is None:
            return
        self._show_temp(self.start_pt, p)

    def _show_temp(self, a: QtCore.QPointF, b: QtCore.QPointF):
        from app.tools.dimension import fmt_ft_inches

        if self.temp is None:
            group = QtWidgets.QGraphicsItemGroup()
            pen = QtGui.QPen(QtGui.QColor("#e0e0e0"))
            pen.setCosmetic(True)
            line = QtWidgets.QGraphicsLineItem()
            line.setPen(pen)
            group.addToGroup(line)
            txt = QtWidgets.QGraphicsSimpleTextItem("")
            txt.setBrush(QtGui.QBrush(QtGui.QColor("#ffd166")))
            txt.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
            group.addToGroup(txt)
            group.setParentItem(self.layer)
            self.temp = (group, line, txt)
        group, line, txt = self.temp
        line.setLine(a.x(), a.y(), b.x(), b.y())
        mid = (a + b) / 2
        txt.setText(fmt_ft_inches(QtCore.QLineF(a, b).length(), self.win.px_per_ft))
        txt.setPos(mid + QtCore.QPointF(8, -8))

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.start_pt is None:
            self.start_pt = p
            return False
        # second point finishes measurement (no persistence)
        self.active = False
        self.start_pt = None
        return True
