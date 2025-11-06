import math


def _almost_equal(a: float, b: float, tol: float = 1e-7) -> bool:
    return abs(a - b) <= tol


def test_arc_from_points_parity():
    """Parity test: legacy vs lv_cad arc_from_points.

    Use separate Point types for each implementation to avoid static
    typing complaints and to exercise the conversion boundary.
    """
    import cad_core.arc as legacy
    from cad_core.lines import Point as LegacyPoint
    from lv_cad.cad_core.arc import arc_from_points as new_arc
    from lv_cad.cad_core.lines import Point as NewPoint

    # legacy inputs
    c_legacy = LegacyPoint(0.0, 0.0)
    a_legacy = LegacyPoint(1.0, 0.0)
    b_legacy = LegacyPoint(0.0, 1.0)
    la = legacy.arc_from_points(c_legacy, a_legacy, b_legacy)

    # new implementation inputs (use the lv_cad Point type)
    c_new = NewPoint(0.0, 0.0)
    a_new = NewPoint(1.0, 0.0)
    b_new = NewPoint(0.0, 1.0)
    na = new_arc(c_new, a_new, b_new)

    pi = math.pi
    assert _almost_equal(la.radius, na.radius)
    assert _almost_equal(la.start_angle % (2 * pi), na.start_angle % (2 * pi))
    assert _almost_equal(la.end_angle % (2 * pi), na.end_angle % (2 * pi))
