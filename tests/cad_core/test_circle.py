import math

from cad_core.lines import Line, Point
from cad_core.circle import Circle, line_circle_intersections, circle_circle_intersections


def test_line_circle_two_points():
    c = Circle(Point(0, 0), 5)
    l = Line(Point(-10, 0), Point(10, 0))
    pts = line_circle_intersections(l, c)
    xs = sorted(p.x for p in pts)
    assert len(pts) == 2 and abs(xs[0] + 5.0) < 1e-9 and abs(xs[1] - 5.0) < 1e-9


def test_circle_circle_two_points():
    c1 = Circle(Point(-5, 0), 5)
    c2 = Circle(Point(5, 0), 5)
    pts = circle_circle_intersections(c1, c2)
    assert len(pts) == 2
    # y coordinates symmetric
    ys = sorted(p.y for p in pts)
    assert abs(ys[0] + ys[1]) < 1e-9

