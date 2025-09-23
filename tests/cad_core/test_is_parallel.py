from cad_core.lines import Line, Point, is_parallel

def test_parallel_lines():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(0, 10), Point(10, 10))
    assert is_parallel(l1, l2) is True

def test_non_parallel_lines():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(0, 0), Point(0, 10))
    assert is_parallel(l1, l2) is False

def test_collinear_lines():
    l1 = Line(Point(0, 0), Point(10, 0))
    l2 = Line(Point(20, 0), Point(30, 0))
    assert is_parallel(l1, l2) is True

def test_nearly_parallel_lines():
    l1 = Line(Point(0, 0), Point(1000, 0))
    l2 = Line(Point(0, 1e-10), Point(1000, 1e-10))
    assert is_parallel(l1, l2) is True
