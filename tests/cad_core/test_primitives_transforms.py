import math

from cad_core.geom.primitives import LineSegment, Point, Vector
from cad_core.geom.transform import rotate, scale, translate


def almost(a: float, b: float, eps: float = 1e-9) -> bool:
    return abs(a - b) <= eps


def test_translate_point_and_vector():
    p = Point(1.0, -2.0)
    v = Vector(3.0, 4.0)

    p2 = translate(p, 2.0, 10.0)
    v2 = translate(v, -1.0, 0.5)

    assert (p2.x, p2.y) == (3.0, 8.0)
    assert (v2.dx, v2.dy) == (2.0, 4.5)


def test_scale_segment():
    seg = LineSegment(Point(1.0, 2.0), Point(-3.0, 4.0))
    seg2 = scale(seg, 2.0, 0.5)

    assert (seg2.a.x, seg2.a.y) == (2.0, 1.0)
    assert (seg2.b.x, seg2.b.y) == (-6.0, 2.0)


def test_rotate_point_90deg_counterclockwise():
    p = Point(1.0, 0.0)
    p2 = rotate(p, math.pi / 2.0)
    assert almost(p2.x, 0.0)
    assert almost(p2.y, 1.0)


def test_rotate_vector_and_segment():
    v = Vector(0.0, 1.0)
    v2 = rotate(v, math.pi)
    assert almost(v2.dx, 0.0)
    assert almost(v2.dy, -1.0)

    seg = LineSegment(Point(1.0, 0.0), Point(0.0, 1.0))
    seg2 = rotate(seg, math.pi / 2.0)
    assert almost(seg2.a.x, 0.0) and almost(seg2.a.y, 1.0)
    assert almost(seg2.b.x, -1.0) and almost(seg2.b.y, 0.0)

