from __future__ import annotations

import math
from dataclasses import dataclass

from .lines import Line, Point, intersection


@dataclass(frozen=True)
class Chamfer:
    line1: Line
    line2: Line
    distance: float


def chamfer_lines(line1: Line, line2: Line, distance: float) -> Line:
    """Creates a chamfer between two lines."""
    intersect_pt = intersection(line1, line2)
    if intersect_pt is None:
        raise ValueError("Lines do not intersect")

    # Get direction vectors
    v1 = Point(line1.b.x - line1.a.x, line1.b.y - line1.a.y)
    v2 = Point(line2.b.x - line2.a.x, line2.b.y - line2.a.y)

    # Normalize vectors
    len1 = math.sqrt(v1.x**2 + v1.y**2)
    v1_norm = Point(v1.x / len1, v1.y / len1)

    len2 = math.sqrt(v2.x**2 + v2.y**2)
    v2_norm = Point(v2.x / len2, v2.y / len2)

    # Points for chamfer line
    p1 = Point(intersect_pt.x - v1_norm.x * distance, intersect_pt.y - v1_norm.y * distance)
    p2 = Point(intersect_pt.x + v2_norm.x * distance, intersect_pt.y + v2_norm.y * distance)

    return Line(p1, p2)


__all__ = ["Chamfer", "chamfer_lines"]
