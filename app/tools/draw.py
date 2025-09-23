from enum import IntEnum
from PySide6 import QtCore, QtGui, QtWidgets
from app.wiring import WireItem

class DrawMode(IntEnum):
    NONE = 0
    LINE = 1
    RECT = 2
    CIRCLE = 3
    POLYLINE = 4
    ARC3 = 5
    WIRE = 6

class DrawController:
    def __init__(self, window, layer):
        self.win = window
        self.layer = layer
        self.mode = DrawMode.NONE
        self.temp_item = None
        self.points = []

    def set_mode(self, mode: DrawMode):
        self.finish()
        self.mode = mode
        self.win.statusBar().showMessage(f"Draw: {mode.name.title()} — click to start, Esc to finish")

    def finish(self):
        # Commit polyline if user ends with Esc and we have >=2 points
        if self.mode == DrawMode.POLYLINE and len(self.points) >= 2:
            path = QtGui.QPainterPath(self.points[0])
            for pt in self.points[1:]:
                path.lineTo(pt)
            it = QtWidgets.QGraphicsPathItem(path)
            pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
            it.setPen(pen); it.setZValue(20); it.setParentItem(self.layer)
            it.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
            it.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        # Cleanup preview
        if self.temp_item and self.temp_item.scene():
            self.temp_item.scene().removeItem(self.temp_item)
        self.temp_item = None
        self.points = []
        self.mode = DrawMode.NONE

    def on_mouse_move(self, pt_scene: QtCore.QPointF, shift_ortho=False):
        if not self.points:
            return
        p0 = self.points[0]
        p1 = QtCore.QPointF(pt_scene)
        if shift_ortho:
            dx = abs(p1.x() - p0.x()); dy = abs(p1.y() - p0.y())
            if dx > dy: p1.setY(p0.y())
            else: p1.setX(p0.x())

        if self.mode in (DrawMode.LINE, DrawMode.WIRE):
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsLineItem()
                col = "#2aa36b" if self.mode==DrawMode.WIRE else "#7aa2f7"
                pen = QtGui.QPen(QtGui.QColor(col)); pen.setCosmetic(True)
                if self.mode==DrawMode.WIRE: pen.setWidth(2)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            if isinstance(self.temp_item, QtWidgets.QGraphicsLineItem):
                self.temp_item.setLine(p0.x(), p0.y(), p1.x(), p1.y())

        elif self.mode == DrawMode.RECT:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsRectItem()
                pen = QtGui.QPen(QtGui.QColor("#7dcfff")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            if isinstance(self.temp_item, QtWidgets.QGraphicsRectItem):
                rect = QtCore.QRectF(p0, p1).normalized()
                self.temp_item.setRect(rect)

        elif self.mode == DrawMode.CIRCLE:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsEllipseItem()
                pen = QtGui.QPen(QtGui.QColor("#bb9af7")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            if isinstance(self.temp_item, QtWidgets.QGraphicsEllipseItem):
                r = QtCore.QLineF(p0, p1).length()
                self.temp_item.setRect(p0.x()-r, p0.y()-r, 2*r, 2*r)

        elif self.mode == DrawMode.POLYLINE:
            if self.temp_item is None:
                self.temp_item = QtWidgets.QGraphicsPathItem()
                pen = QtGui.QPen(QtGui.QColor("#9ece6a")); pen.setCosmetic(True)
                self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
            path = QtGui.QPainterPath(self.points[0])
            for pt in self.points[1:]:
                path.lineTo(pt)
            path.lineTo(p1)
            if isinstance(self.temp_item, QtWidgets.QGraphicsPathItem):
                self.temp_item.setPath(path)
        elif self.mode == DrawMode.ARC3 and len(self.points) == 2:
            # live preview for 3-point arc after two points chosen
            a, b = self.points[0], self.points[1]
            c = p1
            cx, cy, r, start_deg, span_deg = _circle_from_3pts(a, b, c)
            if r > 0:
                if self.temp_item is None:
                    self.temp_item = QtWidgets.QGraphicsPathItem()
                    pen = QtGui.QPen(QtGui.QColor("#bb9af7")); pen.setCosmetic(True)
                    self.temp_item.setPen(pen); self.temp_item.setParentItem(self.layer)
                rect = QtCore.QRectF(cx-r, cy-r, 2*r, 2*r)
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, start_deg)
                path.arcTo(rect, start_deg, span_deg)
                if isinstance(self.temp_item, QtWidgets.QGraphicsPathItem):
                    self.temp_item.setPath(path)

    def on_click(self, pt_scene: QtCore.QPointF, shift_ortho=False):
        if self.mode == DrawMode.NONE:
            return False
        if not self.points:
            self.points = [pt_scene]
            return False
        p0 = self.points[0]; p1 = QtCore.QPointF(pt_scene)
        if shift_ortho:
            dx = abs(p1.x() - p0.x()); dy = abs(p1.y() - p0.y())
            if dx > dy: p1.setY(p0.y())
            else: p1.setX(p0.x())

        if self.mode in (DrawMode.LINE, DrawMode.WIRE, DrawMode.RECT, DrawMode.CIRCLE, DrawMode.ARC3):
            if self.mode in (DrawMode.LINE, DrawMode.WIRE):
                # Create fire alarm specific wire if in wire mode
                if self.mode == DrawMode.WIRE and hasattr(self.win, 'fire_alarm_integrator'):
                    # Default to SLC wire type, but this could be configurable
                    it = WireItem(QtCore.QPointF(p0.x(), p0.y()), QtCore.QPointF(p1.x(), p1.y()), "SLC")
                    it.setParentItem(self.layer)
                    # Notify fire alarm integrator of wire creation
                    self.win.fire_alarm_integrator.on_wire_created(it)
                else:
                    it = QtWidgets.QGraphicsLineItem(p0.x(), p0.y(), p1.x(), p1.y())
            elif self.mode == DrawMode.RECT:
                it = QtWidgets.QGraphicsRectItem(QtCore.QRectF(p0, p1).normalized())
            elif self.mode == DrawMode.CIRCLE:
                r = QtCore.QLineF(p0, p1).length()
                it = QtWidgets.QGraphicsEllipseItem(p0.x()-r, p0.y()-r, 2*r, 2*r)
            else:  # ARC3: need 3rd click to finalize
                if len(self.points) < 2:
                    self.points.append(p1)
                    return False
                a, b = self.points[0], self.points[1]
                c = p1
                cx, cy, r, start_deg, span_deg = _circle_from_3pts(a, b, c)
                if r <= 0:
                    self.finish(); return True
                rect = QtCore.QRectF(cx-r, cy-r, 2*r, 2*r)
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, start_deg)
                path.arcTo(rect, start_deg, span_deg)
                it = QtWidgets.QGraphicsPathItem(path)
            # For non-fire alarm wires, set pen and flags
            if not isinstance(it, WireItem):
                pen = QtGui.QPen(QtGui.QColor("#e0e0e0")); pen.setCosmetic(True)
                if self.mode == DrawMode.WIRE: pen.setWidth(2)
                it.setPen(pen); it.setZValue(20)
                it.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
                it.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
            it.setParentItem(self.layer)
            self.finish()
            return True

        elif self.mode == DrawMode.POLYLINE:
            self.points.append(p1)
            return False
        return False

    # Programmatic helpers for command bar
    def add_point_command(self, pt_scene: QtCore.QPointF) -> bool:
        """Feed a point from command input; returns True if an entity was committed."""
        if self.mode == DrawMode.NONE:
            return False
        if not self.points:
            self.points = [QtCore.QPointF(pt_scene)]
            return False
        return self.on_click(pt_scene, shift_ortho=False)


def _circle_from_3pts(a: QtCore.QPointF, b: QtCore.QPointF, c: QtCore.QPointF):
    # Compute circle through 3 points; return center, radius, and start/span in degrees from point a→b→c
    ax, ay = a.x(), a.y(); bx, by = b.x(), b.y(); cx, cy = c.x(), c.y()
    d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
    if abs(d) < 1e-6:
        return 0.0, 0.0, -1.0, 0.0, 0.0
    ux = ((ax*ax+ay*ay)*(by-cy) + (bx*bx+by*by)*(cy-ay) + (cx*cx+cy*cy)*(ay-by)) / d
    uy = ((ax*ax+ay*ay)*(cx-bx) + (bx*bx+by*by)*(ax-cx) + (cx*cx+cy*cy)*(bx-ax)) / d
    r = QtCore.QLineF(QtCore.QPointF(ux, uy), a).length()
    import math
    def ang(px, py):
        return math.degrees(math.atan2(- (py-uy), (px-ux)))
    a0 = ang(ax, ay); a1 = ang(bx, by); a2 = ang(cx, cy)
    # sweep from a0->a2 passing near a1; choose smaller abs sweep that still passes a1 heuristically
    def norm(x):
        while x <= -180: x += 360
        while x > 180: x -= 360
        return x
    s1 = norm(a1 - a0); s2 = norm(a2 - a0)
    # ensure sweep includes a1 directionally; simple heuristic: use s2 as span
    return ux, uy, r, a0, s2