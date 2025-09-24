from cad_core.arc import Arc
from cad_core.lines import Line, Point, trim_segment_by_arc


def test_trim_segment_by_arc_basic():
    # Arc: radius 5 from 0..pi/2 (x>=0,y>=0 quadrant)
    arc = Arc(center=Point(0, 0), radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    seg = Line(Point(0, 0), Point(10, 0))
    out = trim_segment_by_arc(seg, arc, end="b")
    assert out is not None
    assert abs(out.b.x - 5.0) < 1e-9 and abs(out.b.y - 0.0) < 1e-9


def test_trim_segment_by_arc_noop_when_intersection_behind():
    arc = Arc(center=Point(0, 0), radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    seg = Line(Point(-10, 0), Point(0, 0))
    out = trim_segment_by_arc(seg, arc, end="a")
    # Intersection at (5,0) lies beyond 'a'->'b' shortening direction; expect None
    assert out is None


def test_trim_segment_by_arc_tangent_single_point():
    # Horizontal segment at y=5 ending near x=0 should trim to (0,5)
    arc = Arc(center=Point(0, 0), radius=5.0, start_angle=0.0, end_angle=1.57079632679, ccw=True)
    seg = Line(Point(-1, 5), Point(1, 5))
    out = trim_segment_by_arc(seg, arc, end="b")
    assert out is not None
    assert abs(out.b.x - 0.0) < 1e-9 and abs(out.b.y - 5.0) < 1e-9
