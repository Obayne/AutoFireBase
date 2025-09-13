from __future__ import annotations

import math
from typing import Union

from .primitives import LineSegment, Point, Vector

Geom = Union[Point, Vector, LineSegment]


def translate(g: Geom, tx: float, ty: float) -> Geom:
    if isinstance(g, Point):
        return Point(g.x + tx, g.y + ty)
    if isinstance(g, Vector):
        return Vector(g.dx + tx, g.dy + ty)
    if isinstance(g, LineSegment):
        return LineSegment(translate(g.a, tx, ty), translate(g.b, tx, ty))
    raise TypeError(f"Unsupported geometry: {type(g)!r}")


def scale(g: Geom, sx: float, sy: float) -> Geom:
    if isinstance(g, Point):
        return Point(g.x * sx, g.y * sy)
    if isinstance(g, Vector):
        return Vector(g.dx * sx, g.dy * sy)
    if isinstance(g, LineSegment):
        return LineSegment(scale(g.a, sx, sy), scale(g.b, sx, sy))
    raise TypeError(f"Unsupported geometry: {type(g)!r}")


def rotate(g: Geom, radians: float) -> Geom:
    c = math.cos(radians)
    s = math.sin(radians)

    def rot_xy(x: float, y: float) -> tuple[float, float]:
        return (x * c - y * s, x * s + y * c)

    if isinstance(g, Point):
        x, y = rot_xy(g.x, g.y)
        return Point(x, y)
    if isinstance(g, Vector):
        x, y = rot_xy(g.dx, g.dy)
        return Vector(x, y)
    if isinstance(g, LineSegment):
        return LineSegment(rotate(g.a, radians), rotate(g.b, radians))
    raise TypeError(f"Unsupported geometry: {type(g)!r}")

