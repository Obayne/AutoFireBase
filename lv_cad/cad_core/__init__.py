"""Lightweight CAD core replacement (initial).

This module provides a small subset of the original `cad_core` API used by
the application. It is intentionally minimal — just enough to validate the
strangler workflow and run smoke tests. Real, complete implementations will be
added incrementally in follow-up PRs.
"""

from dataclasses import dataclass
from typing import Optional

__all__ = ["Point", "intersection_line_line"]


@dataclass
class Point:
    x: float
    y: float


def intersection_line_line(a: tuple[Point, Point], b: tuple[Point, Point]) -> Point | None:
    """Return intersection point of two line segments (a and b) or None.

    This is a minimal deterministic implementation used for smoke testing and
    contract verification with legacy code.
    """
    (x1, y1), (x2, y2) = (a[0].x, a[0].y), (a[1].x, a[1].y)
    (x3, y3), (x4, y4) = (b[0].x, b[0].y), (b[1].x, b[1].y)
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-12:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

    # basic bounding check
    def _within(v: float, a_: float, b_: float) -> bool:
        lo = min(a_, b_) - 1e-9
        hi = max(a_, b_) + 1e-9
        return lo <= v <= hi

    if not (
        _within(px, x1, x2) and _within(py, y1, y2) and _within(px, x3, x4) and _within(py, y3, y4)
    ):
        return None
    return Point(px, py)
