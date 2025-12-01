"""
Benchmark suite for cad_core.circle module.

Tests performance of circle-related operations:
- Line-circle intersections
- Circle-circle intersections
- Various geometric configurations
"""

import pytest

from cad_core.circle import Circle, circle_circle_intersections, line_circle_intersections
from cad_core.lines import Line, Point


# Fixtures for common test data
@pytest.fixture
def unit_circle():
    """Circle at origin with radius 1."""
    return Circle(Point(0, 0), 1.0)


@pytest.fixture
def large_circle():
    """Large circle for stress testing."""
    return Circle(Point(0, 0), 1000.0)


@pytest.fixture
def offset_circle():
    """Circle offset from origin."""
    return Circle(Point(50, 50), 25.0)


# ============================================================
# Line-Circle Intersection Benchmarks
# ============================================================


def test_benchmark_line_circle_two_intersections(benchmark, unit_circle):
    """Benchmark line cutting through circle (2 intersections)."""
    line = Line(Point(-2, 0), Point(2, 0))
    result = benchmark(line_circle_intersections, line, unit_circle)
    assert len(result) == 2


def test_benchmark_line_circle_tangent(benchmark, unit_circle):
    """Benchmark tangent line (1 intersection)."""
    line = Line(Point(-2, 1), Point(2, 1))
    result = benchmark(line_circle_intersections, line, unit_circle)
    assert len(result) == 1


def test_benchmark_line_circle_no_intersection(benchmark, unit_circle):
    """Benchmark line missing circle (0 intersections)."""
    line = Line(Point(-2, 5), Point(2, 5))
    result = benchmark(line_circle_intersections, line, unit_circle)
    assert len(result) == 0


def test_benchmark_line_circle_diagonal(benchmark, unit_circle):
    """Benchmark diagonal line through circle."""
    line = Line(Point(-2, -2), Point(2, 2))
    result = benchmark(line_circle_intersections, line, unit_circle)
    assert len(result) == 2


def test_benchmark_line_large_circle(benchmark, large_circle):
    """Benchmark with large circle (real-world CAD scale)."""
    line = Line(Point(-1500, 0), Point(1500, 0))
    result = benchmark(line_circle_intersections, line, large_circle)
    assert len(result) == 2


# ============================================================
# Circle-Circle Intersection Benchmarks
# ============================================================


def test_benchmark_circle_circle_two_points(benchmark):
    """Benchmark two circles intersecting at two points."""
    c1 = Circle(Point(0, 0), 5.0)
    c2 = Circle(Point(8, 0), 5.0)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 2


def test_benchmark_circle_circle_tangent(benchmark):
    """Benchmark two circles touching at one point."""
    c1 = Circle(Point(0, 0), 5.0)
    c2 = Circle(Point(10, 0), 5.0)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 1


def test_benchmark_circle_circle_no_intersection(benchmark):
    """Benchmark two circles not touching."""
    c1 = Circle(Point(0, 0), 5.0)
    c2 = Circle(Point(20, 0), 5.0)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 0


def test_benchmark_circle_circle_one_inside(benchmark):
    """Benchmark one circle inside another."""
    c1 = Circle(Point(0, 0), 10.0)
    c2 = Circle(Point(0, 0), 5.0)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 0


def test_benchmark_circle_circle_offset(benchmark, offset_circle):
    """Benchmark circles at offset positions."""
    c2 = Circle(Point(70, 50), 20.0)
    benchmark(circle_circle_intersections, offset_circle, c2)
    # May or may not intersect


# ============================================================
# Batch Operations Benchmarks
# ============================================================


def test_benchmark_multiple_line_circle_intersections(benchmark, unit_circle):
    """Benchmark finding intersections for multiple lines."""
    lines = [Line(Point(-2, y * 0.2), Point(2, y * 0.2)) for y in range(-10, 11)]

    def find_all_intersections():
        results = []
        for line in lines:
            pts = line_circle_intersections(line, unit_circle)
            results.extend(pts)
        return results

    results = benchmark(find_all_intersections)
    assert len(results) > 0


def test_benchmark_multiple_circle_circle_intersections(benchmark):
    """Benchmark finding intersections for grid of circles."""
    base = Circle(Point(0, 0), 10.0)
    circles = [Circle(Point(x * 5, y * 5), 8.0) for x in range(-3, 4) for y in range(-3, 4)]

    def find_all_intersections():
        results = []
        for circ in circles:
            pts = circle_circle_intersections(base, circ)
            results.extend(pts)
        return results

    results = benchmark(find_all_intersections)
    assert len(results) > 0


# ============================================================
# Stress Test Benchmarks
# ============================================================


def test_benchmark_many_circles_grid(benchmark):
    """Stress test: many circle-circle checks in grid pattern."""
    circles = [Circle(Point(x * 10, y * 10), 7.0) for x in range(10) for y in range(10)]

    def check_all_pairs():
        count = 0
        for i in range(len(circles)):
            for j in range(i + 1, len(circles)):
                pts = circle_circle_intersections(circles[i], circles[j])
                count += len(pts)
        return count

    result = benchmark(check_all_pairs)
    assert result >= 0


def test_benchmark_radial_lines_circle(benchmark):
    """Stress test: radial lines from center through circle."""
    import math

    circle = Circle(Point(0, 0), 50.0)
    lines = []
    for i in range(36):  # Every 10 degrees
        angle = i * math.pi / 18
        dx = 100 * math.cos(angle)
        dy = 100 * math.sin(angle)
        lines.append(Line(Point(-dx, -dy), Point(dx, dy)))

    def find_all_intersections():
        results = []
        for line in lines:
            pts = line_circle_intersections(line, circle)
            results.extend(pts)
        return results

    results = benchmark(find_all_intersections)
    assert len(results) == 72  # Each line crosses twice


# ============================================================
# Edge Case Benchmarks
# ============================================================


def test_benchmark_tiny_circles(benchmark):
    """Benchmark with very small circles (precision test)."""
    c1 = Circle(Point(0, 0), 0.001)
    c2 = Circle(Point(0.0015, 0), 0.001)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 2


def test_benchmark_huge_circles(benchmark):
    """Benchmark with very large circles (numeric stability)."""
    c1 = Circle(Point(0, 0), 1e6)
    c2 = Circle(Point(1.5e6, 0), 1e6)
    result = benchmark(circle_circle_intersections, c1, c2)
    assert len(result) == 2


def test_benchmark_high_precision_tolerance(benchmark):
    """Benchmark with tight tolerance."""
    c1 = Circle(Point(0, 0), 5.0)
    line = Line(Point(-10, 0), Point(10, 0))
    result = benchmark(line_circle_intersections, line, c1, tol=1e-12)
    assert len(result) == 2
