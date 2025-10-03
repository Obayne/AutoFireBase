from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath

try:
    # For type hints only (avoid hard import cycles)
    from .device import DeviceItem  # noqa: F401
except Exception:
    pass


def rebuild_overlay(
    devices_group: QtWidgets.QGraphicsItemGroup,
    overlay_group: QtWidgets.QGraphicsItemGroup,
    size: float = 120.0,
    pen: QtGui.QPen | None = None,
    brush: QtGui.QBrush | None = None,
) -> None:
    """Rebuilds simple coverage glyphs (square with inner circle) centered on each device.
    - size: outer square width/height (scene units)
    """
    # Clear previous overlay
    for it in list(overlay_group.childItems()):
        it.scene().removeItem(it)

    if pen is None:
        pen = QtGui.QPen(QtCore.Qt.darkBlue)
        pen.setCosmetic(True)
        pen.setWidthF(0)
    if brush is None:
        brush = QtGui.QBrush(QtCore.Qt.transparent)

    half = float(size) / 2.0
    inner_r = float(size) * 0.35  # inner circle radius

    for it in devices_group.childItems():
        # Only draw for device-like items having rect()/center()
        if not hasattr(it, "rect"):
            continue
        try:
            c: QPointF = it.rect().center()
        except Exception:
            continue

        # Build square + circle path
        path = QPainterPath()
        rect = QRectF(c.x() - half, c.y() - half, size, size)
        path.addRect(rect)
        path.addEllipse(QRectF(c.x() - inner_r, c.y() - inner_r, inner_r * 2, inner_r * 2))

        gp = QtWidgets.QGraphicsPathItem(path)
        gp.setPen(pen)
        gp.setBrush(brush)
        gp.setZValue(79)  # just beneath devices_group (which is usually 100)
        gp.setParentItem(overlay_group)
