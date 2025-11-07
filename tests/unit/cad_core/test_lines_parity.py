from cad_core.lines import Line, Point


def _almost_equal(p1: Point, p2: Point, tol: float = 1e-7) -> bool:
    return abs(p1.x - p2.x) <= tol and abs(p1.y - p2.y) <= tol


def test_intersection_parity():
    import cad_core.lines as legacy
    from lv_cad.cad_core.lines import intersection_line_line as new_intersect

    l1 = Line(Point(0.0, 0.0), Point(1.0, 1.0))
    l2 = Line(Point(0.0, 1.0), Point(1.0, 0.0))
    r1 = legacy.intersection_line_line(l1, l2)
    r2 = new_intersect(l1, l2)
    assert (r1 is None and r2 is None) or (_almost_equal(r1, r2))


def test_parallel_lines():
    import cad_core.lines as legacy
    from lv_cad.cad_core.lines import is_parallel as new_parallel

    l1 = Line(Point(0.0, 0.0), Point(1.0, 0.0))
    l2 = Line(Point(0.0, 1.0), Point(1.0, 1.0))
    assert legacy.is_parallel(l1, l2)
    assert new_parallel(l1, l2)


def test_nearest_point_and_segment():
    import cad_core.lines as legacy
    from lv_cad.cad_core.lines import nearest_point_on_line as new_nearest
    from lv_cad.cad_core.lines import is_point_on_segment as new_on_seg

    seg = Line(Point(0.0, 0.0), Point(10.0, 0.0))
    p = Point(3.5, 2.0)
    r1 = legacy.nearest_point_on_line(seg, p)
    r2 = new_nearest(seg, p)
    assert abs(r1.x - r2.x) < 1e-7 and abs(r1.y - r2.y) < 1e-7

    pt_on = Point(5.0, 0.0)
    assert legacy.is_point_on_segment(pt_on, seg)
    assert new_on_seg(pt_on, seg)
