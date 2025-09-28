from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets

# Centralized Z-values for drawing layers to keep ordering predictable
Z_UNDERLAY = -50
Z_SKETCH = 40
Z_WIRES = 60
Z_DEVICES = 100
Z_OVERLAY = 200


def _hairline_pen(color: QtGui.QColor | str, width_px: float = 0.0) -> QtGui.QPen:
    col = QtGui.QColor(color) if not isinstance(color, QtGui.QColor) else color
    pen = QtGui.QPen(col)
    pen.setCosmetic(True)
    if width_px > 0:
        pen.setWidthF(float(width_px))
    return pen


@dataclass
class LayerStyle:
    name: str
    color: QtGui.QColor
    width_px: float = 0.0

    def pen(self) -> QtGui.QPen:
        return _hairline_pen(self.color, self.width_px)


class LayerStyleRegistry:
    """Manages CAD layer display styles (pen/brush), providing safe defaults.

    This avoids ad-hoc pen setup scattered across tools and keeps a single
    place to tweak look-and-feel (and to enforce guardrails, e.g., cosmetic lines).
    """

    def __init__(self):
        self._styles: dict[str, LayerStyle] = {}
        # Defaults (dark theme friendly)
        self.register(LayerStyle("sketch", QtGui.QColor("#e0e0e0"), 0.0))
        self.register(LayerStyle("guide", QtGui.QColor("#7aa2f7"), 0.0))
        self.register(LayerStyle("overlay", QtGui.QColor("#c0caf5"), 0.0))
        self.register(LayerStyle("wire", QtGui.QColor("#2aa36b"), 2.0))

    def register(self, style: LayerStyle):
        self._styles[style.name] = style

    def get(self, name: str, fallback: str = "sketch") -> LayerStyle:
        return self._styles.get(name) or self._styles[fallback]


STYLES = LayerStyleRegistry()


def ensure_parent(
    item: QtWidgets.QGraphicsItem, parent_group: QtWidgets.QGraphicsItemGroup, z: float
) -> None:
    """Attach item to a parent group and set Z-order. Safe no-op if already attached."""
    try:
        if item.parentItem() is not parent_group:
            item.setParentItem(parent_group)
        if item.zValue() != z:
            item.setZValue(z)
    except Exception:
        pass


def _finite(v: float) -> bool:
    return v is not None and v == v and v not in (float("inf"), float("-inf"))


def _valid_point(p: QtCore.QPointF) -> bool:
    return _finite(p.x()) and _finite(p.y())


def add_line(
    layer: QtWidgets.QGraphicsItemGroup, a: QtCore.QPointF, b: QtCore.QPointF, style: str = "sketch"
) -> QtWidgets.QGraphicsLineItem | None:
    if not (_valid_point(a) and _valid_point(b)):
        return None
    it = QtWidgets.QGraphicsLineItem(a.x(), a.y(), b.x(), b.y())
    it.setPen(STYLES.get(style).pen())
    ensure_parent(it, layer, Z_SKETCH)
    return it


def add_rect(
    layer: QtWidgets.QGraphicsItemGroup,
    p0: QtCore.QPointF,
    p1: QtCore.QPointF,
    style: str = "sketch",
) -> QtWidgets.QGraphicsRectItem | None:
    if not (_valid_point(p0) and _valid_point(p1)):
        return None
    rect = QtCore.QRectF(p0, p1).normalized()
    it = QtWidgets.QGraphicsRectItem(rect)
    it.setPen(STYLES.get(style).pen())
    it.setBrush(QtCore.Qt.NoBrush)
    ensure_parent(it, layer, Z_SKETCH)
    return it


def add_circle(
    layer: QtWidgets.QGraphicsItemGroup,
    center: QtCore.QPointF,
    radius: float,
    style: str = "sketch",
) -> QtWidgets.QGraphicsEllipseItem | None:
    r = float(radius)
    if not _valid_point(center) or not _finite(r) or r <= 0.0:
        return None
    it = QtWidgets.QGraphicsEllipseItem(center.x() - r, center.y() - r, 2 * r, 2 * r)
    it.setPen(STYLES.get(style).pen())
    it.setBrush(QtCore.Qt.NoBrush)
    ensure_parent(it, layer, Z_SKETCH)
    return it


def add_polyline(
    layer: QtWidgets.QGraphicsItemGroup,
    points: Iterable[QtCore.QPointF],
    style: str = "sketch",
    close: bool = False,
) -> QtWidgets.QGraphicsPathItem | None:
    pts: list[QtCore.QPointF] = [
        QtCore.QPointF(p) for p in points if _valid_point(QtCore.QPointF(p))
    ]
    if len(pts) < 2:
        return None
    path = QtGui.QPainterPath(pts[0])
    for p in pts[1:]:
        path.lineTo(p)
    if close:
        path.closeSubpath()
    it = QtWidgets.QGraphicsPathItem(path)
    it.setPen(STYLES.get(style).pen())
    it.setBrush(QtCore.Qt.NoBrush)
    ensure_parent(it, layer, Z_SKETCH)
    return it


def add_wire(
    layer: QtWidgets.QGraphicsItemGroup, a: QtCore.QPointF, b: QtCore.QPointF
) -> QtWidgets.QGraphicsPathItem | None:
    """Add a thicker, green cosmetic wire segment with guardrails."""
    if not (_valid_point(a) and _valid_point(b)):
        return None
    path = QtGui.QPainterPath(a)
    path.lineTo(b)
    it = QtWidgets.QGraphicsPathItem(path)
    it.setPen(STYLES.get("wire").pen())
    it.setBrush(QtCore.Qt.NoBrush)
    ensure_parent(it, layer, Z_WIRES)
    return it
