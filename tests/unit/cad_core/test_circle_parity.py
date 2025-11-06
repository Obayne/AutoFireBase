def _pt_tuple(p):
    return (round(p.x, 7), round(p.y, 7))


def test_line_circle_parity():
    import cad_core.circle as legacy
    from cad_core.lines import Point as LegacyPoint
    from lv_cad.cad_core.circle import line_circle_intersections as new_line_circle
    from lv_cad.cad_core.lines import Point as NewPoint

    c = legacy.Circle(LegacyPoint(0.0, 0.0), 1.0)
    l = legacy.Line(LegacyPoint(-2.0, 0.0), LegacyPoint(2.0, 0.0))
    la = legacy.line_circle_intersections(l, c)

    cn = from_new = None
    # build new types and call new implementation
    cn = legacy.Circle(NewPoint(0.0, 0.0), 1.0)
    ln = legacy.Line(NewPoint(-2.0, 0.0), NewPoint(2.0, 0.0))
    na = new_line_circle(ln, cn)

    assert set(_pt_tuple(p) for p in la) == set(_pt_tuple(p) for p in na)


def test_circle_circle_parity():
    import cad_core.circle as legacy
    from cad_core.lines import Point as LegacyPoint
    from lv_cad.cad_core.circle import circle_circle_intersections as new_circle_circle
    from lv_cad.cad_core.lines import Point as NewPoint

    c1 = legacy.Circle(LegacyPoint(0.0, 0.0), 1.0)
    c2 = legacy.Circle(LegacyPoint(1.0, 0.0), 1.0)
    la = legacy.circle_circle_intersections(c1, c2)

    c1n = legacy.Circle(NewPoint(0.0, 0.0), 1.0)
    c2n = legacy.Circle(NewPoint(1.0, 0.0), 1.0)
    na = new_circle_circle(c1n, c2n)

    assert set(_pt_tuple(p) for p in la) == set(_pt_tuple(p) for p in na)
