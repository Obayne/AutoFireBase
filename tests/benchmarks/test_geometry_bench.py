from __future__ import annotations

from cad_core.lines import (
    Line,
    Point,
    intersection_line_line,
    intersection_segment_segment,
    trim_segment_by_cutter,
)


def _horiz(a: float, b: float) -> Line:
    return Line(Point(a, 0.0), Point(b, 0.0))


def _vert(x: float, a: float, b: float) -> Line:
    return Line(Point(x, a), Point(x, b))


def test_bench_line_line_intersection(benchmark):
    l1 = Line(Point(0.0, 0.0), Point(10.0, 10.0))
    l2 = Line(Point(0.0, 10.0), Point(10.0, 0.0))

    def run():
        return intersection_line_line(l1, l2)

    ip = benchmark(run)
    assert ip is not None


def test_bench_segment_segment_intersection(benchmark):
    s1 = _horiz(0.0, 100.0)
    s2 = _vert(50.0, -50.0, 50.0)

    def run():
        return intersection_segment_segment(s1, s2)

    ip = benchmark(run)
    assert ip is not None


def test_bench_trim_by_cutter(benchmark):
    seg = _horiz(0.0, 100.0)
    cutter = _vert(75.0, -10.0, 10.0)

    def run():
        return trim_segment_by_cutter(seg, cutter, end="b")

    out = benchmark(run)
    assert out is not None and out.b.x == 75.0
