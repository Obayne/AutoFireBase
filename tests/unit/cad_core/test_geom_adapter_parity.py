from cad_core.lines import Line as LegacyLine, Point as LegacyPoint


def test_segment_intersection_parity():
    import cad_core.geom_adapter as legacy
    from lv_cad.cad_core.geom_adapter import segment_intersection as new_segment_intersection
    from lv_cad.cad_core.lines import Line as NewLine, Point as NewPoint

    s1 = LegacyLine(LegacyPoint(0, 0), LegacyPoint(10, 0))
    s2 = LegacyLine(LegacyPoint(5, -5), LegacyPoint(5, 5))
    la = legacy.segment_intersection(s1, s2)

    s1n = NewLine(NewPoint(0, 0), NewPoint(10, 0))
    s2n = NewLine(NewPoint(5, -5), NewPoint(5, 5))
    na = new_segment_intersection(s1n, s2n)

    assert la is not None and na is not None
    assert abs(la.x - na.x) < 1e-9 and abs(la.y - na.y) < 1e-9


def test_trim_segment_to_intersection_parity():
    import cad_core.geom_adapter as legacy
    from lv_cad.cad_core.geom_adapter import trim_segment_to_intersection as new_trim
    from cad_core.lines import Line as LegacyLine2, Point as LegacyPoint2
    from lv_cad.cad_core.lines import Line as NewLine2, Point as NewPoint2

    s1 = LegacyLine2(LegacyPoint2(0, 0), LegacyPoint2(10, 0))
    s2 = LegacyLine2(LegacyPoint2(7, -2), LegacyPoint2(7, 2))
    la = legacy.trim_segment_to_intersection(s1, s2, end="b")

    s1n = NewLine2(NewPoint2(0, 0), NewPoint2(10, 0))
    s2n = NewLine2(NewPoint2(7, -2), NewPoint2(7, 2))
    na = new_trim(s1n, s2n, end="b")

    assert la is not None and na is not None
    # compare coordinates rather than dataclass equality because the
    # legacy and new Point classes are distinct types
    assert abs(la.a.x - na.a.x) < 1e-9 and abs(la.a.y - na.a.y) < 1e-9
    assert abs(la.b.x - na.b.x) < 1e-9 and abs(la.b.y - na.b.y) < 1e-9
