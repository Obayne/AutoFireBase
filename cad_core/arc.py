from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

from .lines import Point, _sub


@dataclass(frozen=True)
class Arc:
    center: Point
    radius: float
    start_angle: float  # radians
    end_angle: float    # radians
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

