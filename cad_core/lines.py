from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def as_tuple(self) -> Tuple[float, float]:
        return (float(self.x), float(self.y))


@dataclass(frozen=True)
class Line:
    a: Point
    b: Point

    def as_tuple(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        return (self.a.as_tuple(), self.b.as_tuple())


def _sub(p: Point, q: Point) -> Point:
    return Point(p.x - q.x, p.y - q.y)


def _add(p: Point, q: Point) -> Point:
    return Point(p.x + q.x, p.y + q.y)


def _scale(p: Point, s: float) -> Point:
    return Point(p.x * s, p.y * s)


def _cross(p: Point, q: Point) -> float:
    return p.x * q.y - p.y * q.x


def _dot(p: Point, q: Point) -> float:
    return p.x * q.x + p.y * q.y


def intersection_line_line(l1: Line, l2: Line, tol: float = 1e-9) -> Optional[Point]:
    """Return intersection point of two infinite lines, or None if parallel.

    Uses a 2D cross-product formulation. Treats lines as infinite; trimming is separate.
    """

    p = l1.a
    r = _sub(l1.b, l1.a)
    q = l2.a
    s = _sub(l2.b, l2.a)

    rxs = _cross(r, s)
    q_p = _sub(q, p)

    if abs(rxs) < tol:  # Parallel (or nearly)
        return None

    t = _cross(q_p, s) / rxs
    # u = _cross(q_p, r) / rxs  # not needed for the point itself
    return _add(p, _scale(r, t))


def extend_line_end_to_point(line: Line, target: Point, end: str = "b") -> Line:
    """Return a new line where one end ('a' or 'b') is moved to target.

    Does not mutate input; returns a new Line instance.
    """

    if end not in ("a", "b"):
        raise ValueError("end must be 'a' or 'b'")
    if end == "a":
        return Line(a=target, b=line.b)
    return Line(a=line.a, b=target)


def extend_line_to_intersection(line: Line, other: Line, end: str = "b", tol: float = 1e-9) -> Optional[Line]:
    """Extend one end of 'line' to meet the infinite intersection with 'other'.

    Returns a new Line or None if lines are parallel (no intersection).
    """

    ip = intersection_line_line(line, other, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(line, ip, end=end)


__all__ = [
    "Point",
    "Line",
    "intersection_line_line",
    "extend_line_end_to_point",
    "extend_line_to_intersection",
]

