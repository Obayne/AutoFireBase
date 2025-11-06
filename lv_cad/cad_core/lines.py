from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Line:
    a: Point
    b: Point


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


def intersection_line_line(l1: Line, l2: Line, tol: float = 1e-9) -> Point | None:
    """Return intersection point of two infinite lines, or None if parallel.

    Uses a 2D cross-product formulation. Treats lines as infinite; trimming is separate.
    """

    # Accept legacy tests that pass a tuple (Point, Point) as a line
    if not hasattr(l1, "a"):
        if (isinstance(l1, tuple) or isinstance(l1, list)) and len(l1) == 2:
            l1 = Line(a=l1[0], b=l1[1])
        else:
            raise TypeError("l1 must be a Line or a (Point, Point) tuple")
    if not hasattr(l2, "a"):
        if (isinstance(l2, tuple) or isinstance(l2, list)) and len(l2) == 2:
            l2 = Line(a=l2[0], b=l2[1])
        else:
            raise TypeError("l2 must be a Line or a (Point, Point) tuple")

    p = l1.a
    r = _sub(l1.b, l1.a)
    q = l2.a
    s = _sub(l2.b, l2.a)

    rxs = _cross(r, s)
    q_p = _sub(q, p)

    if abs(rxs) < tol:  # Parallel (or nearly)
        return None

    t = _cross(q_p, s) / rxs
    return _add(p, _scale(r, t))


def is_parallel(l1: Line, l2: Line, tol: float = 1e-9) -> bool:
    r = _sub(l1.b, l1.a)
    s = _sub(l2.b, l2.a)
    return abs(_cross(r, s)) < tol


def nearest_point_on_line(line: Line, p: Point) -> Point:
    a, b = line.a, line.b
    ab = _sub(b, a)
    ap = _sub(p, a)
    denom = _dot(ab, ab)
    if denom <= 0:
        return a
    t = _dot(ap, ab) / denom
    return _add(a, _scale(ab, t))


def is_point_on_segment(p: Point, seg: Line, tol: float = 1e-9) -> bool:
    a, b = seg.a, seg.b
    if abs(_cross(_sub(p, a), _sub(b, a))) > tol:
        return False
    ab = _sub(b, a)
    ap = _sub(p, a)
    bp = _sub(p, b)
    return _dot(ap, ab) >= -tol and _dot(bp, _sub(a, b)) >= -tol


def intersection_segment_segment(s1: Line, s2: Line, tol: float = 1e-9) -> Point | None:
    ip = intersection_line_line(s1, s2, tol=tol)
    if ip is None:
        return None
    if is_point_on_segment(ip, s1, tol=tol) and is_point_on_segment(ip, s2, tol=tol):
        return ip
    return None


def extend_line_end_to_point(line: Line, target: Point, end: str = "b") -> Line:
    if end not in ("a", "b"):
        raise ValueError("end must be 'a' or 'b'")
    if end == "a":
        return Line(a=target, b=line.b)
    return Line(a=line.a, b=target)


def extend_line_to_intersection(
    line: Line, other: Line, end: str = "b", tol: float = 1e-9
) -> Line | None:
    ip = intersection_line_line(line, other, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(line, ip, end=end)


def trim_line_by_cut(line: Line, cutter: Line, end: str = "b", tol: float = 1e-9) -> Line | None:
    ip = intersection_line_line(line, cutter, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(line, ip, end=end)


def trim_segment_by_cutter(
    seg: Line, cutter: Line, end: str = "b", tol: float = 1e-9
) -> Line | None:
    ip = intersection_segment_segment(seg, cutter, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(seg, ip, end=end)


__all__ = [
    "Point",
    "Line",
    "is_parallel",
    "intersection_line_line",
    "extend_line_end_to_point",
    "extend_line_to_intersection",
    "trim_line_by_cut",
    "nearest_point_on_line",
    "is_point_on_segment",
    "intersection_segment_segment",
    "trim_segment_by_cutter",
]
