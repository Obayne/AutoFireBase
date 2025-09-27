from cad_core.chamfer import chamfer_lines
from cad_core.lines import Line, Point


def test_chamfer_lines():
    line1 = Line(Point(0, 0), Point(10, 0))
    line2 = Line(Point(10, 0), Point(10, 10))
    chamfer_line = chamfer_lines(line1, line2, 2.0)
    assert chamfer_line.p1 == Point(8, 0)
    assert chamfer_line.p2 == Point(10, 2)
