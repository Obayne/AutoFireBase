from cad_core.lines import (
    Line,
    Point,
    intersection_segment_segment,
    is_point_on_segment,
    trim_segment_by_cutter,
)


def test_point_on_segment_bounds_and_inside():
    s = Line(Point(0, 0), Point(10, 0))
    assert is_point_on_segment(Point(0, 0), s)
    assert is_point_on_segment(Point(10, 0), s)
    assert is_point_on_segment(Point(5, 0), s)
    assert not is_point_on_segment(Point(11, 0), s)
    assert not is_point_on_segment(Point(5, 1e-3), s)


def test_segment_segment_intersection_and_trim():
    s1 = Line(Point(0, 0), Point(10, 0))
    s2 = Line(Point(5, -5), Point(5, 5))
    ip = intersection_segment_segment(s1, s2)
    assert ip is not None and abs(ip.x - 5.0) < 1e-9 and abs(ip.y) < 1e-9

    trimmed = trim_segment_by_cutter(s1, s2, end="b")
    assert trimmed is not None
    assert trimmed.a == s1.a
    assert abs(trimmed.b.x - 5.0) < 1e-9
