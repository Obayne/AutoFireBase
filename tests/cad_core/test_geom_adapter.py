from cad_core.geom_adapter import segment_intersection, trim_segment_to_intersection
from cad_core.lines import Line, Point


def test_segment_intersection_basic():
    s1 = Line(Point(0, 0), Point(10, 0))
    s2 = Line(Point(5, -5), Point(5, 5))
    ip = segment_intersection(s1, s2)
    assert ip is not None and abs(ip.x - 5.0) < 1e-9 and abs(ip.y) < 1e-9


def test_trim_segment_to_intersection_moves_endpoint():
    s1 = Line(Point(0, 0), Point(10, 0))
    s2 = Line(Point(7, -2), Point(7, 2))
    out = trim_segment_to_intersection(s1, s2, end="b")
    assert out is not None
    assert out.a == s1.a
    assert abs(out.b.x - 7.0) < 1e-9
