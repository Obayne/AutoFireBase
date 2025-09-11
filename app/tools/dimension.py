from PySide6 import QtCore, QtGui, QtWidgets

def fmt_ft_inches(px: float, px_per_ft: float) -> str:
    ft = px / px_per_ft if px_per_ft > 0 else 0.0
    sign = '-' if ft < 0 else ''
    ft = abs(ft); whole = int(ft); inches = (ft - whole) * 12.0
    return f"{sign}{whole}'-{inches:.1f}\""

class LinearDimension(QtWidgets.QGraphicsItemGroup):
    def __init__(self, p0: QtCore.QPointF, p1: QtCore.QPointF, px_per_ft: float):
        super().__init__()
        self.p0 = QtCore.QPointF(p0); self.p1 = QtCore.QPointF(p1)
        self.px_per_ft = px_per_ft
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
        self.line = QtWidgets.QGraphicsLineItem(self.p0.x(), self.p0.y(), self.p1.x(), self.p1.y())
        self.line.setPen(pen); self.addToGroup(self.line)
        mid = (self.p0 + self.p1) / 2
        txt = fmt_ft_inches(QtCore.QLineF(self.p0, self.p1).length(), self.px_per_ft)
        self.label = QtWidgets.QGraphicsSimpleTextItem(txt)
        self.label.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.label.setBrush(QtGui.QBrush(QtGui.QColor("#c0caf5")))
        self.label.setPos(mid + QtCore.QPointF(8, -8))
        self.addToGroup(self.label)

class DimensionTool:
    def __init__(self, window, overlay_layer):
        self.win = window
        self.layer = overlay_layer
        self.active = False
        self.start_pt = None

    def start(self):
        self.active = True
        self.start_pt = None
        self.win.statusBar().showMessage("Dimension: click first point, then second point")

    def on_mouse_move(self, p: QtCore.QPointF):
        pass

    def on_click(self, p: QtCore.QPointF):
        if not self.active:
            return False
        if self.start_pt is None:
            self.start_pt = p
            return False
        dim = LinearDimension(self.start_pt, p, self.win.px_per_ft)
        dim.setParentItem(self.layer)
        self.active = False
        self.start_pt = None
        self.win.statusBar().showMessage("Dimension placed")
        return True
