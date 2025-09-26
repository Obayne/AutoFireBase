import math

from cad_core.circle import Circle
from cad_core.fillet import fillet_circle_circle, fillet_line_circle, fillet_line_line
from cad_core.lines import Line, Point


def dist(a: Point, b: Point) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def test_fillet_perpendicular_lines_radius2():
    l1 = Line(Point(-10, 0), Point(10, 0))
    l2 = Line(Point(0, -10), Point(0, 10))
    r = 2.0
    res = fillet_line_line(l1, l2, r)
    assert res is not None
    p1, p2, c = res
    # Both tangent points must be at the same distance from intersection (t = r * tan(45°) = r)
    I = Point(0.0, 0.0)
    assert abs(dist(p1, I) - r) < 1e-6
    assert abs(dist(p2, I) - r) < 1e-6
    # Center should be at distance r / sin(45°) = r * sqrt(2)
    assert abs(dist(c, I) - r * math.sqrt(2)) < 1e-6


def test_fillet_parallel_returns_none():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(0, 1), Point(10, 1))
    assert fillet_line_line(l1, l2, 2.0) is None


def test_fillet_line_circle_candidates_nonempty():
    c = Circle(Point(0, 0), 5.0)
    l = Line(Point(-10, 0), Point(10, 0))
    out = fillet_line_circle(l, c, 2.0)
    assert isinstance(out, list) and len(out) >= 1


def test_fillet_circle_circle_candidates_nonempty():
    c1 = Circle(Point(-5, 0), 5.0)
    c2 = Circle(Point(5, 0), 5.0)
    out = fillet_circle_circle(c1, c2, 2.0)
    assert isinstance(out, list)
    assert len(out) >= 1
