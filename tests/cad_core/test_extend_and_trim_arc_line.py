from cad_core.arc import Arc
from cad_core.circle import Circle
from cad_core.lines import Line, Point, extend_segment_to_circle, trim_line_by_arc


def test_extend_segment_to_circle_picks_nearest_intersection():
    seg = Line(Point(0, 0), Point(1, 0))
    circ = Circle(Point(0, 0), 5.0)
    out = extend_segment_to_circle(seg, circ, end="b")
    assert out is not None
    assert out.a == seg.a
    assert abs(out.b.x - 5.0) < 1e-9 and abs(out.b.y - 0.0) < 1e-9


def test_trim_line_by_arc_uses_arc_sweep():
    # Arc: radius 5 from angle 0 to pi/2 CCW (quadrant I)
    center = Point(0, 0)
    arc = Arc(center=center, radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    # Line along x-axis
    base = Line(Point(0, 0), Point(10, 0))
    out = trim_line_by_arc(base, arc, end="b")
    assert out is not None
    assert abs(out.b.x - 5.0) < 1e-9 and abs(out.b.y - 0.0) < 1e-9

    # Negative-x segment: trimming 'a' should not jump across to +x arc point
    base2 = Line(Point(-10, 0), Point(0, 0))
    out2 = trim_line_by_arc(base2, arc, end="a")
    assert out2 is None
