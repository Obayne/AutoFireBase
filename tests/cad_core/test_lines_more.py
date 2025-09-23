from cad_core.lines import Line, Point, intersection_line_line


def test_intersection_tolerates_near_parallel_small_tol():
    # Two lines with very small angle; ensure we can still compute with default tol
    l1 = Line(Point(0, 0), Point(1000, 0))
    l2 = Line(Point(500, -1e-6), Point(500, 1e-6))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 500.0) < 1e-6


def test_simple_intersection():
    l1 = Line(Point(0, 0), Point(10, 10))
    l2 = Line(Point(0, 10), Point(10, 0))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 5.0) < 1e-9
    assert abs(ip.y - 5.0) < 1e-9

def test_horizontal_vertical_intersection():
    l1 = Line(Point(0, 5), Point(10, 5))
    l2 = Line(Point(5, 0), Point(5, 10))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 5.0) < 1e-9
    assert abs(ip.y - 5.0) < 1e-9

def test_collinear_lines():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(20, 0), Point(30, 0))
    ip = intersection_line_line(l1, l2)
    assert ip is None

def test_intersection_at_endpoint():
    l1 = Line(Point(0, 0), Point(10, 10))
    l2 = Line(Point(10, 10), Point(20, 0))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 10.0) < 1e-9
    assert abs(ip.y - 10.0) < 1e-9

def test_large_coordinates():
    l1 = Line(Point(1e6, 1e6), Point(1e6 + 10, 1e6 + 10))
    l2 = Line(Point(1e6, 1e6 + 10), Point(1e6 + 10, 1e6))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - (1e6 + 5.0)) < 1e-9
    assert abs(ip.y - (1e6 + 5.0)) < 1e-9
