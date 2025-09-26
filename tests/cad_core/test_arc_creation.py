import math

import pytest

from cad_core.arc import arc_from_3_points
from cad_core.lines import Point


def test_arc_from_3_points_simple_ccw():
    """Test a simple counter-clockwise arc."""
    p1 = Point(10, 0)
    p2 = Point(0, 10)
    p3 = Point(-10, 0)
    arc = arc_from_3_points(p1, p2, p3)
    assert arc.center == Point(0, 0)
    assert math.isclose(arc.radius, 10.0)
    assert math.isclose(arc.start_angle, 0.0)
    assert math.isclose(arc.end_angle, math.pi)
    assert arc.ccw is True


def test_arc_from_3_points_simple_cw():
    """Test a simple clockwise arc."""
    p1 = Point(10, 0)
    p2 = Point(0, -10)
    p3 = Point(-10, 0)
    arc = arc_from_3_points(p1, p2, p3)
    assert arc.center == Point(0, 0)
    assert math.isclose(arc.radius, 10.0)
    assert math.isclose(arc.start_angle, 0.0)
    assert math.isclose(arc.end_angle, math.pi)
    assert arc.ccw is False


def test_arc_from_3_points_collinear():
    """Test that collinear points raise a ValueError."""
    p1 = Point(0, 0)
    p2 = Point(1, 1)
    p3 = Point(2, 2)
    with pytest.raises(ValueError):
        arc_from_3_points(p1, p2, p3)
