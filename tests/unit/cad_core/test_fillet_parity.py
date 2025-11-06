from cad_core.lines import Line, Point


def _almost_equal(p1: Point, p2: Point, tol: float = 1e-7) -> bool:
    return abs(p1.x - p2.x) <= tol and abs(p1.y - p2.y) <= tol


def _compare_results(
    r1: tuple[Point, Point, Point] | None, r2: tuple[Point, Point, Point] | None, tol: float = 1e-7
) -> bool:
    if r1 is None or r2 is None:
        return r1 is None and r2 is None
    # tuple of three Points
    return (
        _almost_equal(r1[0], r2[0], tol)
        and _almost_equal(r1[1], r2[1], tol)
        and _almost_equal(r1[2], r2[2], tol)
    )


def test_perpendicular_lines_parity():
    import cad_core.fillet as legacy
    from lv_cad.cad_core.fillet import fillet_line_line as new_fillet

    l1 = Line(Point(-1.0, 0.0), Point(1.0, 0.0))
    l2 = Line(Point(0.0, -1.0), Point(0.0, 1.0))
    r = 0.5
    legacy_res = legacy.fillet_line_line(l1, l2, r)
    new_res = new_fillet(l1, l2, r)
    assert _compare_results(legacy_res, new_res)


def test_shallow_angle_lines_parity():
    import cad_core.fillet as legacy
    from lv_cad.cad_core.fillet import fillet_line_line as new_fillet

    # One horizontal, one slight angle
    l1 = Line(Point(-10.0, 0.0), Point(10.0, 0.0))
    l2 = Line(Point(0.0, 0.0), Point(10.0, 1.0))
    r = 0.1
    legacy_res = legacy.fillet_line_line(l1, l2, r)
    new_res = new_fillet(l1, l2, r)
    assert _compare_results(legacy_res, new_res)


def test_parallel_lines_none():
    import cad_core.fillet as legacy
    from lv_cad.cad_core.fillet import fillet_line_line as new_fillet

    l1 = Line(Point(0.0, 0.0), Point(1.0, 0.0))
    l2 = Line(Point(0.0, 1.0), Point(1.0, 1.0))
    r = 0.5
    assert legacy.fillet_line_line(l1, l2, r) is None
    assert new_fillet(l1, l2, r) is None


def test_radius_too_small_none():
    import cad_core.fillet as legacy
    from lv_cad.cad_core.fillet import fillet_line_line as new_fillet

    l1 = Line(Point(-1.0, 0.0), Point(1.0, 0.0))
    l2 = Line(Point(0.0, -1.0), Point(0.0, 1.0))
    r = 0.0
    assert legacy.fillet_line_line(l1, l2, r) is None
    assert new_fillet(l1, l2, r) is None
