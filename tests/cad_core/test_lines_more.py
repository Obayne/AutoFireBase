from cad_core.lines import Line, Point, intersection_line_line


def test_intersection_tolerates_near_parallel_small_tol():
    # Two lines with very small angle; ensure we can still compute with default tol
    l1 = Line(Point(0, 0), Point(1000, 0))
    l2 = Line(Point(500, -1e-6), Point(500, 1e-6))
    ip = intersection_line_line(l1, l2)
    assert ip is not None
    assert abs(ip.x - 500.0) < 1e-6

