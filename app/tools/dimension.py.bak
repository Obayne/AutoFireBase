from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF
from app import units

class DimensionItem(QtWidgets.QGraphicsItemGroup):
    def __init__(self, a: QPointF, b: QPointF, px_per_ft: float):
        super().__init__()
        self.a = QPointF(a); self.b = QPointF(b); self.px_per_ft = px_per_ft
        self.line = QtWidgets.QGraphicsLineItem()
        pen = QtGui.QPen(Qt.black); pen.setCosmetic(True)
        self.line.setPen(pen); self.addToGroup(self.line)

        self.arrow1 = QtWidgets.QGraphicsLineItem(); self.arrow2 = QtWidgets.QGraphicsLineItem()
        for ar in (self.arrow1, self.arrow2):
            ar.setPen(pen); self.addToGroup(ar)

        self.text = QtWidgets.QGraphicsSimpleTextItem("")
        self.text.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations, True)
        self.addToGroup(self.text); self.update_geom()

    def set_points(self, a: QPointF, b: QPointF):
        self.a = QPointF(a); self.b = QPointF(b); self.update_geom()

    def update_geom(self):
        self.line.setLine(self.a.x(), self.a.y(), self.b.x(), self.b.y())
        import math
        ang = math.atan2(self.b.y()-self.a.y(), self.b.x()-self.a.x())
        L = 10.0; bx, by = self.b.x(), self.b.y()
        left  = QtCore.QPointF(bx - L*math.cos(ang-0.35), by - L*math.sin(ang-0.35))
        right = QtCore.QPointF(bx - L*math.cos(ang+0.35), by - L*math.sin(ang+0.35))
        self.arrow1.setLine(bx, by, left.x(), left.y())
        self.arrow2.setLine(bx, by, right.x(), right.y())
        dist_px = (QtCore.QLineF(self.a, self.b)).length()
        dist_ft = units.px_to_ft(dist_px, self.px_per_ft)
        self.text.setText(units.fmt_ft_inches(dist_ft))
        mid = (self.a + self.b) / 2.0
        self.text.setPos(mid + QtCore.QPointF(8, -8))

class DimensionTool:
    def __init__(self, window, layer_overlay):
        self.win = window; self.layer = layer_overlay
        self.dim_item = None; self.active = False; self.start_pt = None

    def start(self):
        self.finish(); self.active = True
        self.win.statusBar().showMessage("Dimension: click start point, then end point. Esc to cancel.")

    def on_mouse_move(self, sp, **kwargs):
        if not self.active or self.dim_item is None: return
        self.dim_item.set_points(self.start_pt, sp)

    def on_click(self, sp, **kwargs):
        if not self.active: return False
        if self.dim_item is None:
            self.start_pt = sp
            self.dim_item = DimensionItem(sp, sp, self.win.px_per_ft)
            self.dim_item.setParentItem(self.layer)
            return False
        else:
            self.dim_item.set_points(self.start_pt, sp)
            self.win.push_history(); self.active = False; self.win.statusBar().showMessage("")
            return True

    def finish(self):
        self.active = False; self.dim_item = None; self.start_pt = None
