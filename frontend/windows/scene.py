"""
Scene Management - CAD Canvas and View System
"""

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

# Default grid size for CAD canvas
DEFAULT_GRID_SIZE = 12.0


class GridScene(QGraphicsScene):
    """CAD scene with grid and snap functionality."""

    def __init__(
        self, grid_size=DEFAULT_GRID_SIZE, x=0, y=0, width=15000, height=10000, parent=None
    ):
        super().__init__(x, y, width, height, parent)
        self.grid_size = grid_size
        self.snap_enabled = True

    def drawBackground(self, painter, rect):
        """Draw grid background."""
        if self.grid_size <= 0:
            return

        # Set up pen for grid lines
        pen = QtGui.QPen(QtGui.QColor("#e0e0e0"))
        pen.setCosmetic(True)
        painter.setPen(pen)

        # Calculate grid bounds
        left = int(rect.left() / self.grid_size) * self.grid_size
        right = int(rect.right() / self.grid_size) * self.grid_size
        top = int(rect.top() / self.grid_size) * self.grid_size
        bottom = int(rect.bottom() / self.grid_size) * self.grid_size

        # Draw vertical lines
        for x in range(int(left), int(right) + 1, int(self.grid_size)):
            painter.drawLine(x, top, x, bottom)

        # Draw horizontal lines
        for y in range(int(top), int(bottom) + 1, int(self.grid_size)):
            painter.drawLine(left, y, right, y)


class CanvasView(QGraphicsView):
    """CAD canvas view with zoom and pan functionality."""

    def __init__(self, scene, devices_group, wires_group, sketch_group, overlay_group, window_ref):
        super().__init__(scene)
        self.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Store references to layer groups
        self.devices_group = devices_group
        self.wires_group = wires_group
        self.sketch_group = sketch_group
        self.overlay_group = overlay_group
        self.win = window_ref

        # Zoom settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        new_zoom = self.zoom_factor * zoom_factor
        if self.min_zoom <= new_zoom <= self.max_zoom:
            self.scale(zoom_factor, zoom_factor)
            self.zoom_factor = new_zoom

    def mousePressEvent(self, event):
        """Handle mouse press for panning."""
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            fake_event = QtGui.QMouseEvent(
                QtCore.QEvent.Type.MouseButtonPress,
                event.pos(),
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.KeyboardModifier.NoModifier,
            )
            super().mousePressEvent(fake_event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
