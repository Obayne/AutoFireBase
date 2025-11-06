from __future__ import annotations

from shapely.geometry import LineString
from shapely.geometry import Point as SPoint

from .lines import Line, Point


def _to_linestring(seg: Line) -> LineString:
    return LineString([(seg.a.x, seg.a.y), (seg.b.x, seg.b.y)])


def _to_point(sp: SPoint) -> Point:
    return Point(float(sp.x), float(sp.y))


def segment_intersection(seg1: Line, seg2: Line) -> Point | None:
    """Return intersection point of two finite segments using Shapely (None if disjoint)."""
    a = _to_linestring(seg1)
    b = _to_linestring(seg2)
    if not a.intersects(b):
        return None
    inter = a.intersection(b)
    # Accept single point intersections only (ignore overlaps/lines)
    if inter.geom_type == "Point":
        return _to_point(inter)
    return None


def trim_segment_to_intersection(seg: Line, cutter: Line, end: str = "b") -> Line | None:
    """Trim a finite segment to its intersection with a cutter segment.

    Returns a new segment or None if there is no intersection.
    """
    sp = segment_intersection(seg, cutter)
    if sp is None:
        return None
    if end == "a":
        return Line(Point(sp.x, sp.y), seg.b)
    return Line(seg.a, Point(sp.x, sp.y))


__all__ = ["segment_intersection", "trim_segment_to_intersection"]
