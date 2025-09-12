from __future__ import annotations

import math
from PySide6 import QtGui

from cad_core.arc import Arc


def path_from_arc(arc: Arc) -> QtGui.QPainterPath:
    cx, cy = arc.center.x, arc.center.y
    r = arc.radius
    start_deg = math.degrees(arc.start_angle)
    end_deg = math.degrees(arc.end_angle)
    if arc.ccw:
        sweep = (end_deg - start_deg) % 360.0
    else:
        sweep = -((start_deg - end_deg) % 360.0)

    rect = QtGui.QRectF(cx - r, cy - r, 2 * r, 2 * r)
    path = QtGui.QPainterPath()
    # Move to start point to avoid auto-connecting
    sx = cx + r * math.cos(math.radians(start_deg))
    sy = cy + r * math.sin(math.radians(start_deg))
    path.moveTo(sx, sy)
    path.arcTo(rect, start_deg, sweep)
    return path

