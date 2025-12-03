from __future__ import annotations

from lv_cad.geometry.point import Point
from lv_cad.operations.fillet import fillet_line_line_native


def test_fillet_line_line_native_perpendicular() -> None:
    # Horizontal and vertical lines crossing at origin
    a1, a2 = Point(-100.0, 0.0), Point(100.0, 0.0)
    b1, b2 = Point(0.0, -100.0), Point(0.0, 100.0)
    r = 5.0

    res = fillet_line_line_native(a1, a2, b1, b2, r)
    assert res is not None
    t1, c, t2 = res

    # Expected magnitudes irrespective of quadrant: |(r,0)| and |(0,r)|; center at |(r,r)|
    coords = {(round(abs(p.x), 6), round(abs(p.y), 6)) for p in (t1, t2)}
    assert (5.0, 0.0) in coords and (0.0, 5.0) in coords
    assert (round(abs(c.x), 6), round(abs(c.y), 6)) == (5.0, 5.0)
