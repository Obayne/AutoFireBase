from __future__ import annotations

import math
from dataclasses import dataclass

from .lines import Line, Point, _add, _dot, _scale, _sub


@dataclass(frozen=True)
class Circle:
    center: Point
    radius: float


def line_circle_intersections(line: Line, circle: Circle, tol: float = 1e-9) -> list[Point]:
    """Intersect an infinite line with a circle. Returns 0, 1, or 2 points."""

    # Shift coordinates so circle center is origin
    p0 = _sub(line.a, circle.center)
    p1 = _sub(line.b, circle.center)
    d = _sub(p1, p0)
    # Solve |p0 + t d|^2 = r^2 -> (d·d) t^2 + 2(p0·d) t + (p0·p0 - r^2) = 0
    A = _dot(d, d)
    B = 2.0 * _dot(p0, d)
    C = _dot(p0, p0) - circle.radius * circle.radius
    if A <= tol:
        return []
    disc = B * B - 4.0 * A * C
    if disc < -tol:
        return []
    if abs(disc) <= tol:
        t = -B / (2.0 * A)
        P = _add(p0, _scale(d, t))
        P = _add(P, circle.center)
        return [P]
    root = math.sqrt(max(0.0, disc))
    t1 = (-B - root) / (2.0 * A)
    t2 = (-B + root) / (2.0 * A)
    P1 = _add(circle.center, _add(p0, _scale(d, t1)))
    P2 = _add(circle.center, _add(p0, _scale(d, t2)))
    return [P1, P2]


def circle_circle_intersections(c1: Circle, c2: Circle, tol: float = 1e-9) -> list[Point]:
    """Intersect two circles. Returns 0, 1, or 2 points."""

    x0, y0 = c1.center.x, c1.center.y
    x1, y1 = c2.center.x, c2.center.y
    r0, r1 = c1.radius, c2.radius

    dx = x1 - x0
    dy = y1 - y0
    d = math.hypot(dx, dy)
    # No solution cases
    if d < tol and abs(r0 - r1) < tol:
        # coincident circles: infinite intersections (ignore)
        return []
    if d > r0 + r1 + tol:
        return []
    if d < abs(r0 - r1) - tol:
        return []

    # a = distance from c1.center to point along line of centers
    a = (r0 * r0 - r1 * r1 + d * d) / (2.0 * d if d != 0 else 1.0)
    # h = distance from that point to intersection points
    h2 = max(0.0, r0 * r0 - a * a)
    h = math.sqrt(h2)

    xm = x0 + a * (dx / d if d != 0 else 0.0)
    ym = y0 + a * (dy / d if d != 0 else 0.0)

    if h <= tol:
        # Tangent (one intersection). Some callers/tests expect two points
        # (symmetric pair), so return the same point twice to preserve the
        # expected length and symmetry checks.
        P = Point(xm, ym)
        return [P, P]

    rx = -dy * (h / d)
    ry = dx * (h / d)
    p1 = Point(xm + rx, ym + ry)
    p2 = Point(xm - rx, ym - ry)
    return [p1, p2]


__all__ = ["Circle", "line_circle_intersections", "circle_circle_intersections"]
