from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def as_tuple(self) -> tuple[float, float]:
        return (float(self.x), float(self.y))


@dataclass(frozen=True)
class Line:
    a: Point
    b: Point

    def as_tuple(self) -> tuple[tuple[float, float], tuple[float, float]]:
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


def intersection_line_line(l1: Line, l2: Line, tol: float = 1e-9) -> Point | None:
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


def is_parallel(l1: Line, l2: Line, tol: float = 1e-9) -> bool:
    """Return True if the direction vectors of the lines are parallel within tol."""
    r = _sub(l1.b, l1.a)
    s = _sub(l2.b, l2.a)
    return abs(_cross(r, s)) <= tol


def nearest_point_on_line(line: Line, p: Point) -> Point:
    """Return the closest point to p on the infinite line through line.a->line.b."""
    a, b = line.a, line.b
    ab = _sub(b, a)
    ap = _sub(p, a)
    denom = _dot(ab, ab)
    if denom <= 0:
        return a
    t = _dot(ap, ab) / denom
    return _add(a, _scale(ab, t))


def is_point_on_segment(p: Point, seg: Line, tol: float = 1e-9) -> bool:
    """Check if point p lies on the segment seg within tolerance."""
    a, b = seg.a, seg.b
    # Collinearity: cross((p-a),(b-a)) ~ 0
    if abs(_cross(_sub(p, a), _sub(b, a))) > tol:
        return False
    # Within bounds via dot-products
    ab = _sub(b, a)
    ap = _sub(p, a)
    bp = _sub(p, b)
    return _dot(ap, ab) >= -tol and _dot(bp, _sub(a, b)) >= -tol


def intersection_segment_segment(s1: Line, s2: Line, tol: float = 1e-9) -> Point | None:
    """Intersection point of two finite segments, or None."""
    ip = intersection_line_line(s1, s2, tol=tol)
    if ip is None:
        return None
    if is_point_on_segment(ip, s1, tol=tol) and is_point_on_segment(ip, s2, tol=tol):
        return ip
    return None


def extend_line_end_to_point(line: Line, target: Point, end: str = "b") -> Line:
    """Return a new line where one end ('a' or 'b') is moved to target.

    Does not mutate input; returns a new Line instance.
    """

    if end not in ("a", "b"):
        raise ValueError("end must be 'a' or 'b'")
    if end == "a":
        return Line(a=target, b=line.b)
    return Line(a=line.a, b=target)


def extend_line_to_intersection(
    line: Line, other: Line, end: str = "b", tol: float = 1e-9
) -> Line | None:
    """Extend one end of 'line' to meet the infinite intersection with 'other'.

    Returns a new Line or None if lines are parallel (no intersection).
    """

    ip = intersection_line_line(line, other, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(line, ip, end=end)


def trim_line_by_cut(line: Line, cutter: Line, end: str = "b", tol: float = 1e-9) -> Line | None:
    """Trim a line segment towards its intersection with a cutter.

    If the infinite lines intersect, this moves the chosen endpoint of `line`
    to the intersection point. Returns None if lines are parallel (no cut).
    Note: This does not check whether the intersection lies within the cutter
    segment bounds; callers may enforce segment-vs-segment rules upstream.
    """
    ip = intersection_line_line(line, cutter, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(line, ip, end=end)


def trim_segment_by_cutter(
    seg: Line, cutter: Line, end: str = "b", tol: float = 1e-9
) -> Line | None:
    """Trim a finite segment to the intersection with a cutter segment.

    Returns new segment or None if no valid intersection lies on both segments.
    """
    ip = intersection_segment_segment(seg, cutter, tol=tol)
    if ip is None:
        return None
    return extend_line_end_to_point(seg, ip, end=end)


def extend_segment_to_circle(
    seg: Line, circle: Circle, end: str = "b", tol: float = 1e-9
) -> Line | None:
    """Extend one end of a segment to the nearest intersection with a circle.

    Returns a new segment or None if the supporting line does not intersect the circle.
    """
    # Local import to avoid circular dependency at module import time
    from .circle import line_circle_intersections

    ips = line_circle_intersections(seg, circle, tol=tol)
    if not ips:
        return None
    endpoint = seg.b if end == "b" else seg.a
    other = seg.a if end == "b" else seg.b
    # For extend, move from endpoint outward along segment direction
    v = _sub(endpoint, other)
    denom = _dot(v, v)
    if denom <= tol:
        return None
    cand = []
    for p in ips:
        t = _dot(_sub(p, endpoint), v) / denom
        if t >= -tol:
            cand.append(p)
    if not cand:
        return None
    target = min(cand, key=lambda p: (p.x - endpoint.x) ** 2 + (p.y - endpoint.y) ** 2)
    return extend_line_end_to_point(seg, target, end=end)


def trim_line_by_arc(line: Line, arc: Arc, end: str = "b", tol: float = 1e-9) -> Line | None:
    """Trim a line to the nearest intersection with a finite arc.

    Intersects the supporting line with the arc's circle and picks the closest
    intersection that lies on the arc sweep. Returns None if there is none.
    """
    # Local imports to avoid circular dependency
    from .arc import is_point_on_arc
    from .circle import Circle, line_circle_intersections

    circle = Circle(arc.center, arc.radius)
    ips = [
        p
        for p in line_circle_intersections(line, circle, tol=tol)
        if is_point_on_arc(arc, p, tol=tol)
    ]
    if not ips:
        return None
    endpoint = line.b if end == "b" else line.a
    other = line.a if end == "b" else line.b
    w = _sub(other, endpoint)
    denom = _dot(w, w)
    if denom <= tol:
        return None
    cand = []
    for p in ips:
        t = _dot(_sub(p, endpoint), w) / denom
        if -tol <= t <= 1 + tol:
            cand.append(p)
    if not cand:
        return None
    target = min(cand, key=lambda p: (p.x - endpoint.x) ** 2 + (p.y - endpoint.y) ** 2)
    return extend_line_end_to_point(line, target, end=end)


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

__all__ += [
    "extend_segment_to_circle",
    "trim_line_by_arc",
]


def extend_segment_to_arc(seg: Line, arc: Arc, end: str = "b", tol: float = 1e-9) -> Line | None:
    """Extend a segment endpoint to the nearest intersection that lies on the arc sweep.

    Extends the chosen endpoint forward along the segment direction; returns None if no
    suitable intersection exists on the finite arc.
    """
    # Local imports to avoid circular dependency
    from .arc import is_point_on_arc
    from .circle import Circle, line_circle_intersections

    circle = Circle(arc.center, arc.radius)
    ips = [
        p
        for p in line_circle_intersections(seg, circle, tol=tol)
        if is_point_on_arc(arc, p, tol=tol)
    ]
    if not ips:
        return None
    endpoint = seg.b if end == "b" else seg.a
    other = seg.a if end == "b" else seg.b
    # For extension, move from endpoint outward along segment direction
    v = _sub(endpoint, other)
    denom = _dot(v, v)
    if denom <= tol:
        return None
    cand = []
    for p in ips:
        t = _dot(_sub(p, endpoint), v) / denom
        if t >= -tol:
            cand.append(p)
    if not cand:
        return None
    target = min(cand, key=lambda p: (p.x - endpoint.x) ** 2 + (p.y - endpoint.y) ** 2)
    return extend_line_end_to_point(seg, target, end=end)


__all__ += ["extend_segment_to_arc"]
