import math

from cad_core.arc import arc_from_points
from cad_core.lines import Point


def test_arc_from_points():
    center = Point(0, 0)
    p_start = Point(10, 0)
    p_end = Point(0, 10)
    arc = arc_from_points(center, p_start, p_end)
    assert arc.center == center
    assert math.isclose(arc.radius, 10.0)
    assert math.isclose(arc.start_angle, 0.0)
    assert math.isclose(arc.end_angle, math.pi / 2)
    assert arc.ccw is True
