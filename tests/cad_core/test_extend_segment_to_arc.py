from cad_core.arc import Arc
from cad_core.lines import Line, Point, extend_segment_to_arc


def test_extend_segment_to_arc_basic():
    # Arc: radius 5 in quadrant I (0..pi/2)
    arc = Arc(center=Point(0, 0), radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    seg = Line(Point(0, 0), Point(1, 0))
    out = extend_segment_to_arc(seg, arc, end="b")
    assert out is not None
    assert out.a == seg.a
    assert abs(out.b.x - 5.0) < 1e-9 and abs(out.b.y - 0.0) < 1e-9


def test_extend_segment_to_arc_respects_arc_sweep():
    # Arc in quadrant I; segment pointing to negative x should not jump across
    arc = Arc(center=Point(0, 0), radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    seg = Line(Point(-1, 0), Point(-2, 0))
    assert extend_segment_to_arc(seg, arc, end="b") is None
