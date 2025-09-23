from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from .point import Point
from .units import almost_equal


@dataclass(frozen=True)
class Segment:
    a: Point
    b: Point

    def length(self) -> float:
        return self.a.distance_to(self.b)

    def midpoint(self) -> Point:
        return Point((self.a.x + self.b.x) / 2.0, (self.a.y + self.b.y) / 2.0)


def _sub(p: Point, q: Point) -> Point:
    return Point(p.x - q.x, p.y - q.y)


def _cross(p: Point, q: Point) -> float:
    return p.x * q.y - p.y * q.x


def _dot(p: Point, q: Point) -> float:
    return p.x * q.x + p.y * q.y


def _orientation(a: Point, b: Point, c: Point, tol: float = 1e-9) -> int:
    """Return orientation of triplet (a,b,c): 0 collinear, 1 cw, 2 ccw."""
    val = _cross(_sub(b, a), _sub(c, a))
    if abs(val) <= tol:
        return 0
    return 2 if val > 0 else 1


def _on_segment(a: Point, b: Point, c: Point, tol: float = 1e-9) -> bool:
    """Check if point c lies on segment ab (inclusive), within tolerance."""
    if _orientation(a, b, c, tol=tol) != 0:
        return False
    return (
        min(a.x, b.x) - tol <= c.x <= max(a.x, b.x) + tol
        and min(a.y, b.y) - tol <= c.y <= max(a.y, b.y) + tol
    )


def intersection(seg1: Segment, seg2: Segment, tol: float = 1e-9) -> Optional[Point]:
    """Return intersection point of two segments, or None.

    Handles proper intersections and endpoint touches; overlapping collinear
    segments return None (no unique intersection point).
    """
    a1, a2 = seg1.a, seg1.b
    b1, b2 = seg2.a, seg2.b

    o1 = _orientation(a1, a2, b1, tol)
    o2 = _orientation(a1, a2, b2, tol)
    o3 = _orientation(b1, b2, a1, tol)
    o4 = _orientation(b1, b2, a2, tol)

    # General case
    if o1 != o2 and o3 != o4:
        # Compute intersection via line-line parametric form
        p = a1
        r = _sub(a2, a1)
        q = b1
        s = _sub(b2, b1)
        rxs = _cross(r, s)
        if almost_equal(rxs, 0.0, tol=tol):
            return None
        t = _cross(_sub(q, p), s) / rxs
        return Point(p.x + t * r.x, p.y + t * r.y)

    # Special Cases: collinear + on-segment endpoints
    if o1 == 0 and _on_segment(a1, a2, b1, tol):
        return b1
    if o2 == 0 and _on_segment(a1, a2, b2, tol):
        return b2
    if o3 == 0 and _on_segment(b1, b2, a1, tol):
        return a1
    if o4 == 0 and _on_segment(b1, b2, a2, tol):
        return a2

    # Collinear overlapping without a unique single point
    return None


def project_point(seg: Segment, p: Point) -> Point:
    """Project point p onto infinite line through seg and clamp to segment bounds."""
    a, b = seg.a, seg.b
    ab = _sub(b, a)
    ap = _sub(p, a)
    denom = _dot(ab, ab)
    if denom <= 0:
        return a
    t = _dot(ap, ab) / denom
    if t < 0:
        return a
    if t > 1:
        return b
    return Point(a.x + t * ab.x, a.y + t * ab.y)

