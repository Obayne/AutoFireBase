from __future__ import annotations

import math
from dataclasses import dataclass

from .lines import Point, _sub


@dataclass(frozen=True)
class Arc:
    center: Point
    radius: float
    start_angle: float  # radians
    end_angle: float  # radians
    ccw: bool = True


def _angle(center: Point, p: Point) -> float:
    v = _sub(p, center)
    return math.atan2(v.y, v.x)


def arc_from_points(center: Point, p_start: Point, p_end: Point, prefer_short: bool = True) -> Arc:
    r = math.hypot(p_start.x - center.x, p_start.y - center.y)
    a1 = _angle(center, p_start)
    a2 = _angle(center, p_end)
    # Normalize to [0, 2pi)
    a1n = (a1 + 2 * math.pi) % (2 * math.pi)
    a2n = (a2 + 2 * math.pi) % (2 * math.pi)
    if prefer_short:
        # Choose direction that yields the smaller sweep
        cw_sweep = (a1n - a2n) % (2 * math.pi)
        ccw_sweep = (a2n - a1n) % (2 * math.pi)
        if ccw_sweep <= cw_sweep:
            return Arc(center, r, a1n, a2n, ccw=True)
        else:
            return Arc(center, r, a2n, a1n, ccw=False)
    # Default CCW
    return Arc(center, r, a1n, a2n, ccw=True)


def arc_from_3_points(p1: Point, p2: Point, p3: Point) -> Arc:
    """Create an arc through three points with normalized angles.

    Always reports start/end angles corresponding to p1 and p3 respectively,
    normalized to [0, 2π). The `ccw` flag indicates direction.
    """
    # Circle center via determinant formulation
    A = p1.x * (p2.y - p3.y) - p1.y * (p2.x - p3.x) + p2.x * p3.y - p3.x * p2.y
    B = (
        (p1.x**2 + p1.y**2) * (p3.y - p2.y)
        + (p2.x**2 + p2.y**2) * (p1.y - p3.y)
        + (p3.x**2 + p3.y**2) * (p2.y - p1.y)
    )
    C = (
        (p1.x**2 + p1.y**2) * (p2.x - p3.x)
        + (p2.x**2 + p2.y**2) * (p3.x - p1.x)
        + (p3.x**2 + p3.y**2) * (p1.x - p2.x)
    )

    if abs(A) < 1e-9:
        raise ValueError("Points are collinear")

    cx = -B / (2 * A)
    cy = -C / (2 * A)
    center = Point(cx, cy)

    radius = math.hypot(p1.x - cx, p1.y - cy)

    def norm(a: float) -> float:
        two_pi = 2 * math.pi
        return (a + two_pi) % two_pi

    start_angle = norm(math.atan2(p1.y - cy, p1.x - cx))
    end_angle = norm(math.atan2(p3.y - cy, p3.x - cx))

    # CCW if signed area of (p1,p2,p3) is positive
    signed_area = (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)
    ccw = signed_area > 0

    return Arc(center, radius, start_angle, end_angle, ccw=ccw)


__all__ = ["Arc", "arc_from_points", "arc_from_3_points"]
