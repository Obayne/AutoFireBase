from PySide6 import QtWidgets
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QPainterPath, QPen


class WireItem(QtWidgets.QGraphicsPathItem):
    def __init__(self, a: QPointF, b: QPointF):
        super().__init__()
        path = QPainterPath(a)
        path.lineTo(b)
        self.setPath(path)
        pen = QPen(Qt.darkGreen)
        pen.setWidth(2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setZValue(60)

    def to_json(self):
        p = self.path()
        a = p.elementAt(0)
        b = p.elementAt(1)
        return {"ax": a.x, "ay": a.y, "bx": b.x, "by": b.y}
