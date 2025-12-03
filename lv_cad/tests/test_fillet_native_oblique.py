from __future__ import annotations

import math

from lv_cad.geometry.point import Point
from lv_cad.operations.fillet import fillet_line_line_native
from lv_cad.util.numeric import assert_close


def _norm(x: float, y: float) -> float:
    return math.hypot(x, y)


def _dot(ax: float, ay: float, bx: float, by: float) -> float:
    return ax * bx + ay * by


def test_fillet_line_line_native_oblique() -> None:
    # Lines: u along +X; v at +60 degrees
    a1, a2 = Point(-100.0, 0.0), Point(100.0, 0.0)
    ang = math.radians(60.0)
    vdir = (math.cos(ang), math.sin(ang))
    b1, b2 = Point(0.0, 0.0), Point(100.0 * vdir[0], 100.0 * vdir[1])

    r = 10.0
    res = fillet_line_line_native(a1, a2, b1, b2, r)
    assert res is not None
    t1, c, t2 = res

    # Radius constraint: distances CT1 and CT2 equal r
    d1 = _norm(t1.x - c.x, t1.y - c.y)
    d2 = _norm(t2.x - c.x, t2.y - c.y)
    assert_close(d1, r)
    assert_close(d2, r)

    # Perpendicularity: (T1-C) ⟂ u, (T2-C) ⟂ v
    u = (1.0, 0.0)
    tc1 = (t1.x - c.x, t1.y - c.y)
    tc2 = (t2.x - c.x, t2.y - c.y)
    assert abs(_dot(tc1[0], tc1[1], u[0], u[1])) <= 1e-6
    assert abs(_dot(tc2[0], tc2[1], vdir[0], vdir[1])) <= 1e-6

    # Center on bisector: (C - I) direction equals normalize(u+v)
    I = Point(0.0, 0.0)
    w = (u[0] + vdir[0], u[1] + vdir[1])
    wn = _norm(w[0], w[1])
    w = (w[0] / wn, w[1] / wn)
    ci = (c.x - I.x, c.y - I.y)
    cin = _norm(ci[0], ci[1])
    ciu = (ci[0] / cin, ci[1] / cin)
    # Direction match up to sign
    assert abs(_dot(ciu[0], ciu[1], w[0], w[1])) >= 1 - 1e-6
