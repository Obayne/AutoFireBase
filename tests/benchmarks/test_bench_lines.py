"""
Benchmark suite for cad_core.lines module.

Tests performance of critical geometry operations:
- Line-line intersection
- Point-on-line operations
- Segment operations
- Parallel checks
"""

import pytest

from cad_core.lines import (
    Line,
    Point,
    intersection_line_line,
    intersection_segment_segment,
    is_parallel,
    is_point_on_segment,
    nearest_point_on_line,
)


# Fixtures for common test data
@pytest.fixture
def simple_lines():
    """Simple perpendicular lines for basic tests."""
    return (
        Line(Point(0, 0), Point(10, 0)),  # Horizontal
        Line(Point(5, -5), Point(5, 5)),  # Vertical
    )


@pytest.fixture
def diagonal_lines():
    """Diagonal lines with varying angles."""
    return (
        Line(Point(0, 0), Point(100, 100)),  # 45 degrees
        Line(Point(0, 100), Point(100, 0)),  # -45 degrees
    )


@pytest.fixture
def parallel_lines():
    """Parallel horizontal lines."""
    return (
        Line(Point(0, 0), Point(100, 0)),
        Line(Point(0, 10), Point(100, 10)),
    )


@pytest.fixture
def large_coords():
    """Lines with large coordinate values (real-world CAD)."""
    return (
        Line(Point(1000.5, 2000.75), Point(5000.25, 3000.5)),
        Line(Point(2500.125, 1000.375), Point(3500.875, 4000.625)),
    )


# ============================================================
# Line-Line Intersection Benchmarks
# ============================================================


def test_benchmark_intersection_simple(benchmark, simple_lines):
    """Benchmark intersection of perpendicular lines."""
    l1, l2 = simple_lines
    result = benchmark(intersection_line_line, l1, l2)
    assert result is not None


def test_benchmark_intersection_diagonal(benchmark, diagonal_lines):
    """Benchmark intersection of diagonal lines."""
    l1, l2 = diagonal_lines
    result = benchmark(intersection_line_line, l1, l2)
    assert result is not None


def test_benchmark_intersection_parallel(benchmark, parallel_lines):
    """Benchmark parallel line check (no intersection)."""
    l1, l2 = parallel_lines
    result = benchmark(intersection_line_line, l1, l2)
    assert result is None


def test_benchmark_intersection_large_coords(benchmark, large_coords):
    """Benchmark intersection with large coordinate values."""
    l1, l2 = large_coords
    benchmark(intersection_line_line, l1, l2)
    # May or may not intersect, just testing performance


# ============================================================
# Parallel Check Benchmarks
# ============================================================


def test_benchmark_is_parallel_true(benchmark, parallel_lines):
    """Benchmark parallel check for actually parallel lines."""
    l1, l2 = parallel_lines
    result = benchmark(is_parallel, l1, l2)
    assert result is True


def test_benchmark_is_parallel_false(benchmark, simple_lines):
    """Benchmark parallel check for perpendicular lines."""
    l1, l2 = simple_lines
    result = benchmark(is_parallel, l1, l2)
    assert result is False


def test_benchmark_is_parallel_near_parallel(benchmark):
    """Benchmark parallel check for nearly parallel lines (edge case)."""
    # Lines with very small angle difference
    l1 = Line(Point(0, 0), Point(100, 0))
    l2 = Line(Point(0, 1), Point(100, 1.001))  # Almost parallel
    benchmark(is_parallel, l1, l2)
    # Result depends on tolerance


# ============================================================
# Point Operations Benchmarks
# ============================================================


def test_benchmark_nearest_point_perpendicular(benchmark):
    """Benchmark finding nearest point perpendicular to line."""
    line = Line(Point(0, 0), Point(10, 0))
    point = Point(5, 5)
    result = benchmark(nearest_point_on_line, line, point)
    assert result.y < 1e-9  # Should be on the line


def test_benchmark_nearest_point_on_line(benchmark):
    """Benchmark when point is already on the line."""
    line = Line(Point(0, 0), Point(10, 0))
    point = Point(5, 0)
    result = benchmark(nearest_point_on_line, line, point)
    assert abs(result.x - 5) < 1e-9


def test_benchmark_nearest_point_diagonal(benchmark):
    """Benchmark nearest point with diagonal line."""
    line = Line(Point(0, 0), Point(100, 100))
    point = Point(50, 0)
    result = benchmark(nearest_point_on_line, line, point)
    assert result is not None


def test_benchmark_is_point_on_segment(benchmark):
    """Benchmark checking if point is on segment."""
    segment = Line(Point(0, 0), Point(10, 0))
    point = Point(5, 0)
    result = benchmark(is_point_on_segment, point, segment)
    assert result is True


def test_benchmark_segment_intersection(benchmark):
    """Benchmark segment-segment intersection."""
    s1 = Line(Point(0, 0), Point(10, 10))
    s2 = Line(Point(0, 10), Point(10, 0))
    result = benchmark(intersection_segment_segment, s1, s2)
    assert result is not None


# ============================================================
# Batch Operations Benchmarks
# ============================================================


def test_benchmark_multiple_intersections(benchmark):
    """Benchmark finding intersections for multiple line pairs."""
    lines = [Line(Point(0, i), Point(100, i)) for i in range(20)]  # 20 horizontal lines
    vertical = Line(Point(50, -10), Point(50, 110))

    def find_all_intersections():
        results = []
        for line in lines:
            pt = intersection_line_line(line, vertical)
            if pt:
                results.append(pt)
        return results

    results = benchmark(find_all_intersections)
    assert len(results) == 20


def test_benchmark_parallel_checks_batch(benchmark):
    """Benchmark checking multiple lines for parallelism."""
    base_line = Line(Point(0, 0), Point(100, 0))
    test_lines = [Line(Point(0, i), Point(100, i if i % 3 == 0 else i + 0.5)) for i in range(50)]

    def check_all_parallel():
        results = []
        for line in test_lines:
            results.append(is_parallel(base_line, line))
        return results

    results = benchmark(check_all_parallel)
    assert len(results) == 50


# ============================================================
# Stress Test Benchmarks
# ============================================================


def test_benchmark_intersection_stress_random_lines(benchmark):
    """Stress test: many intersections with varying angles."""
    import math

    lines = []
    for i in range(100):
        angle = i * math.pi / 50  # Varying angles
        dx = 10 * math.cos(angle)
        dy = 10 * math.sin(angle)
        lines.append(Line(Point(0, 0), Point(dx, dy)))

    def find_all_pairs_intersections():
        count = 0
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                pt = intersection_line_line(lines[i], lines[j])
                if pt:
                    count += 1
        return count

    result = benchmark(find_all_pairs_intersections)
    assert result > 0  # Most should intersect at origin


# ============================================================
# Precision Benchmarks
# ============================================================


def test_benchmark_intersection_high_precision(benchmark):
    """Benchmark with tight tolerance for high precision."""
    l1 = Line(Point(0.000001, 0.000001), Point(10.000001, 0.000001))
    l2 = Line(Point(5.0000005, -5.0000005), Point(5.0000005, 5.0000005))

    result = benchmark(intersection_line_line, l1, l2, tol=1e-12)
    assert result is not None


# ============================================================
# Configuration and Reporting
# ============================================================

# Benchmark configuration via pytest.ini or command line:
# pytest tests/benchmarks/ --benchmark-only
# pytest tests/benchmarks/ --benchmark-autosave
# pytest tests/benchmarks/ --benchmark-compare
