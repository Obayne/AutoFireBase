import math

from cad_core.lines import Line, Point
from cad_core.fillet import fillet_segments_line_line


def test_fillet_segments_perpendicular_radius2():
    # Two perpendicular segments crossing at origin
    s1 = Line(Point(-10, 0), Point(10, 0))
    s2 = Line(Point(0, -10), Point(0, 10))
    pick1 = Point(10, 0)   # near +X end of s1
    pick2 = Point(0, 10)   # near +Y end of s2
    out = fillet_segments_line_line(s1, s2, pick1, pick2, radius=2.0)
    assert out is not None
    ns1, ns2, arc = out
    # Endpoints should have moved to 2 units from origin along each axis
    assert abs(ns1.b.x - 2.0) < 1e-6 and abs(ns1.b.y - 0.0) < 1e-6
    assert abs(ns2.b.x - 0.0) < 1e-6 and abs(ns2.b.y - 2.0) < 1e-6
    # Arc center expected at distance r*sqrt(2) from origin
    cx, cy = arc.center.x, arc.center.y
    assert abs(math.hypot(cx, cy) - (2.0 * math.sqrt(2))) < 1e-6
    # Arc radius equals 2
    assert abs(arc.radius - 2.0) < 1e-6

