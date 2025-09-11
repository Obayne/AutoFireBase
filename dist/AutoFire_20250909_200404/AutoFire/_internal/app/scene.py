
from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_GRID_SIZE = 40  # pixels

class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, *args):
        super().__init__(*args)
        self.grid_size = int(grid_size or DEFAULT_GRID_SIZE)
        self.snap_enabled = True
        self.snap_step_px = 0.0  # if >0, override grid with exact inch-step in px
        self.show_grid = True
        self.setSceneRect(0,0,12000,9000)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        if not self.show_grid: return
        grid = self.grid_size
        left = int(rect.left()) - (int(rect.left()) % grid)
        top = int(rect.top()) - (int(rect.top()) % grid)
        lines = []
        for x in range(left, int(rect.right())+grid, grid):
            lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        for y in range(top, int(rect.bottom())+grid, grid):
            lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
        pen = QtGui.QPen(QtGui.QColor(90,90,90))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawLines(lines)

    def snap(self, p: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return QtCore.QPointF(p)
        # fine step snap
        if self.snap_step_px and self.snap_step_px > 0:
            sx = round(p.x() / self.snap_step_px) * self.snap_step_px
            sy = round(p.y() / self.snap_step_px) * self.snap_step_px
            return QtCore.QPointF(sx, sy)
        # grid intersections
        g = float(self.grid_size or DEFAULT_GRID_SIZE)
        sx = round(p.x() / g) * g
        sy = round(p.y() / g) * g
        return QtCore.QPointF(sx, sy)
