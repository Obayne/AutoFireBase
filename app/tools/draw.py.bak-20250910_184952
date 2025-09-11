# Draw tools (absolute-import safe). Modes: 0=NONE, 1=LINE, 2=RECT, 3=CIRCLE, 4=POLYLINE
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QPointF, QRectF

class DrawMode:
    NONE = 0
    LINE = 1
    RECT = 2
    CIRCLE = 3
    POLYLINE = 4

class DrawController:
    def __init__(self, window, sketch_group):
        self.win = window
        self.group = sketch_group
        self.mode = DrawMode.NONE
        self.temp_item = None
        self.points = []  # for polyline

    def set_mode(self, mode: int):
        self.finish()
        self.mode = mode
        self.win.statusBar().showMessage({DrawMode.LINE:"Line",DrawMode.RECT:"Rect",DrawMode.CIRCLE:"Circle",DrawMode.POLYLINE:"Polyline"}.get(mode,"None"))

    def finish(self):
        if self.temp_item is not None:
            self.temp_item = None
        self.points = []
        self.mode = DrawMode.NONE

    def on_mouse_move(self, scene_pt: QPointF, shift_ortho: bool=False):
        if self.mode == DrawMode.NONE:
            return
        if self.mode in (DrawMode.LINE, DrawMode.RECT, DrawMode.CIRCLE) and self.points:
            p0 = self.points[0]
            p1 = QPointF(scene_pt.x(), scene_pt.y())
            if shift_ortho:
                dx = abs(p1.x() - p0.x()); dy = abs(p1.y() - p0.y())
                if dx > dy: p1.setY(p0.y())
                else: p1.setX(p0.x())
            self._update_temp_shape(p0, p1)

        if self.mode == DrawMode.POLYLINE and self.points:
            # Update last segment preview (optional)
            pass

    def on_click(self, scene_pt: QPointF, shift_ortho: bool=False) -> bool:
        if self.mode == DrawMode.NONE:
            return False

        if self.mode in (DrawMode.LINE, DrawMode.RECT, DrawMode.CIRCLE):
            if not self.points:
                self.points = [scene_pt]
                return False
            # second click: commit
            p0 = self.points[0]
            p1 = QPointF(scene_pt.x(), scene_pt.y())
            if shift_ortho:
                dx = abs(p1.x() - p0.x()); dy = abs(p1.y() - p0.y())
                if dx > dy: p1.setY(p0.y())
                else: p1.setX(p0.x())
            self._commit_shape(p0, p1)
            self.points = []
            return True

        if self.mode == DrawMode.POLYLINE:
            if not self.points:
                self.points = [scene_pt]
                self._start_polyline(scene_pt)
                return False
            else:
                self._extend_polyline(scene_pt)
                # End on double-click is handled by finish() via Esc or menu
                return True

        return False

    # ---- helpers ----
    def _update_temp_shape(self, p0: QPointF, p1: QPointF):
        # For simplicity, use commit each move for preview (fast enough for small scenes)
        self._remove_last_preview()
        item = None
        if self.mode == DrawMode.LINE:
            path = QtGui.QPainterPath(p0); path.lineTo(p1)
            item = QtWidgets.QGraphicsPathItem(path)
        elif self.mode == DrawMode.RECT:
            rect = QRectF(min(p0.x(),p1.x()), min(p0.y(),p1.y()), abs(p1.x()-p0.x()), abs(p1.y()-p0.y()))
            path = QtGui.QPainterPath(); path.addRect(rect); item = QtWidgets.QGraphicsPathItem(path)
        elif self.mode == DrawMode.CIRCLE:
            r = ((p1.x()-p0.x())**2 + (p1.y()-p0.y())**2) ** 0.5
            rect = QRectF(p0.x()-r, p0.y()-r, 2*r, 2*r)
            path = QtGui.QPainterPath(); path.addEllipse(rect); item = QtWidgets.QGraphicsPathItem(path)
        if item:
            pen = QtGui.QPen(Qt.blue); pen.setCosmetic(True); item.setPen(pen); item.setParentItem(self.group)
            self.temp_item = item

    def _commit_shape(self, p0: QPointF, p1: QPointF):
        self._update_temp_shape(p0, p1)
        self.temp_item = None  # leave it on the scene

    def _remove_last_preview(self):
        if self.temp_item is not None:
            self.temp_item.scene().removeItem(self.temp_item)
            self.temp_item = None

    def _start_polyline(self, pt: QPointF):
        path = QtGui.QPainterPath(pt)
        item = QtWidgets.QGraphicsPathItem(path)
        pen = QtGui.QPen(Qt.darkGreen); pen.setCosmetic(True); item.setPen(pen); item.setParentItem(self.group)
        self.temp_item = item

    def _extend_polyline(self, pt: QPointF):
        if not isinstance(self.temp_item, QtWidgets.QGraphicsPathItem):
            self._start_polyline(pt); return
        path = self.temp_item.path()
        path.lineTo(pt)
        self.temp_item.setPath(path)