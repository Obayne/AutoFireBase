from cad_core.lines import (
    Line,
    Point,
    intersection_line_line,
    extend_line_to_intersection,
    trim_line_by_cut,
)


def test_line_line_intersection_basic():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(5, -5), Point(5, 5))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 5.0) < 1e-9
    assert abs(ip.y - 0.0) < 1e-9


def test_line_line_parallel_returns_none():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(0, 1), Point(10, 1))
    assert intersection_line_line(l1, l2) is None


def test_extend_line_to_intersection_moves_endpoint():
    base = Line(Point(0, 0), Point(1, 0))
    other = Line(Point(5, -5), Point(5, 5))
    extended = extend_line_to_intersection(base, other, end="b")
    assert extended is not None
    assert extended.a == base.a
    assert abs(extended.b.x - 5.0) < 1e-9
    assert abs(extended.b.y - 0.0) < 1e-9


def test_trim_line_by_cut_same_as_extend_here():
    base = Line(Point(0, 0), Point(1, 0))
    cutter = Line(Point(5, -5), Point(5, 5))
    trimmed = trim_line_by_cut(base, cutter, end="b")
    assert trimmed is not None
    assert trimmed.a == base.a
    assert abs(trimmed.b.x - 5.0) < 1e-9

