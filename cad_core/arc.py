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


__all__ = ["Arc", "arc_from_points"]


def _norm_angle(a: float) -> float:
    import math

    a = a % (2 * math.pi)
    if a < 0:
        a += 2 * math.pi
    return a


def is_point_on_arc(arc: Arc, p: Point, tol: float = 1e-9) -> bool:
    """Return True if point p lies on the finite arc within tolerance.

    Checks radial distance ~ radius and angular position within start/end sweep.
    """
    import math

    # Check radial distance
    r = math.hypot(p.x - arc.center.x, p.y - arc.center.y)
    if abs(r - arc.radius) > tol:
        return False

    a = _angle(arc.center, p)
    a0 = _norm_angle(arc.start_angle)
    a1 = _norm_angle(arc.end_angle)
    ap = _norm_angle(a)

    if arc.ccw:
        # CCW sweep from a0 to a1
        if a0 <= a1:
            return a0 - tol <= ap <= a1 + tol
        # Wrap through 2*pi
        return ap >= a0 - tol or ap <= a1 + tol
    else:
        # CW sweep from a0 down to a1
        if a1 <= a0:
            return a1 - tol <= ap <= a0 + tol
        # Wrap through 0
        return ap <= a0 + tol or ap >= a1 - tol


__all__ += ["is_point_on_arc"]
