from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_GRID_SIZE = 24  # pixels between minor lines


class GridScene(QtWidgets.QGraphicsScene):
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grid_size = max(2, int(grid_size))
        self.show_grid = True
        self.snap_enabled = True
        self.snap_step_px = 0.0  # if >0, overrides grid intersections

        # Style (preferences can override via setters)
        self.grid_opacity = 0.35  # 0..1
        self.grid_width = 0.0  # 0 = hairline; otherwise widthF in px
        self.major_every = 5

        # Base colors (dark theme)
        self.col_minor_rgb = QtGui.QColor(120, 130, 145)  # we apply alpha every frame
        self.col_major_rgb = QtGui.QColor(160, 170, 185)
        self.col_axis_rgb = QtGui.QColor(180, 190, 205)

    def set_grid_style(self, opacity: float = None, width: float = None, major_every: int = None):
        if opacity is not None:
            self.grid_opacity = max(0.05, min(1.0, float(opacity)))
        if width is not None:
            self.grid_width = max(0.0, float(width))
        if major_every is not None:
            self.major_every = max(2, int(major_every))
        self.update()

    # simple grid snap
    def snap(self, pt: QtCore.QPointF) -> QtCore.QPointF:
        if not self.snap_enabled:
            return pt
        if self.snap_step_px and self.snap_step_px > 0:
            s = self.snap_step_px
            x = round(pt.x() / s) * s
            y = round(pt.y() / s) * s
            return QtCore.QPointF(x, y)
        # snap to grid intersections
        g = self.grid_size
        x = round(pt.x() / g) * g
        y = round(pt.y() / g) * g
        return QtCore.QPointF(x, y)

    def _pen(self, base_rgb: QtGui.QColor):
        c = QtGui.QColor(base_rgb)
        c.setAlphaF(self.grid_opacity)
        pen = QtGui.QPen(c)
        pen.setCosmetic(True)
        if self.grid_width > 0.0:
            pen.setWidthF(self.grid_width)
        return pen

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        super().drawBackground(painter, rect)
        if not self.show_grid or self.grid_size <= 0:
            return

        g = self.grid_size
        left = int(rect.left()) - (int(rect.left()) % g)
        top = int(rect.top()) - (int(rect.top()) % g)

        pen_minor = self._pen(self.col_minor_rgb)
        pen_major = self._pen(self.col_major_rgb)
        major_every = self.major_every

        painter.save()
        # verticals
        x = left
        idx = 0
        while x < rect.right():
            painter.setPen(pen_major if (idx % major_every == 0) else pen_minor)
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += g
            idx += 1
        # horizontals
        y = top
        idy = 0
        while y < rect.bottom():
            painter.setPen(pen_major if (idy % major_every == 0) else pen_minor)
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += g
            idy += 1

        # axes cross at (0,0)
        axis_pen = self._pen(self.col_axis_rgb)
        painter.setPen(axis_pen)
        painter.drawLine(0, int(rect.top()), 0, int(rect.bottom()))
        painter.drawLine(int(rect.left()), 0, int(rect.right()), 0)
        painter.restore()


class CanvasView(QtWidgets.QGraphicsView):
    """Graphics view for CAD canvas with device and layer management."""

    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setMouseTracking(True)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # Store references to groups and window
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.win = window_ref
