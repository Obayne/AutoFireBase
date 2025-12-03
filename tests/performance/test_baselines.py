"""Performance baseline tests for AutoFire CAD operations.

These tests establish performance baselines and detect regressions.
Run with: pytest tests/performance/ -v --benchmark-only

Note: Install pytest-benchmark first: pip install pytest-benchmark
"""

import pytest

from cad_core.fillet import fillet_line_line
from cad_core.lines import Line, Point


class TestPerformanceBaselines:
    """Performance baseline tests for core CAD operations."""

    @pytest.mark.benchmark
    def test_line_creation_baseline(self, benchmark):
        """Baseline: Line object creation."""

        def create_line():
            return Line(Point(0, 0), Point(100, 100))

        result = benchmark(create_line)
        assert result is not None
        # Baseline: ~1-10 microseconds per line

    @pytest.mark.benchmark
    def test_fillet_perpendicular_baseline(self, benchmark):
        """Baseline: Fillet operation on perpendicular lines."""

        def run_fillet():
            line1 = Line(Point(0, 0), Point(100, 0))
            line2 = Line(Point(100, 0), Point(100, 100))
            return fillet_line_line(line1, line2, radius=10.0)

        result = benchmark(run_fillet)
        assert result is not None
        # Baseline: ~10-50 microseconds per fillet

    @pytest.mark.benchmark
    def test_fillet_oblique_baseline(self, benchmark):
        """Baseline: Fillet operation on oblique lines."""

        def run_fillet():
            line1 = Line(Point(0, 0), Point(100, 50))
            line2 = Line(Point(100, 50), Point(150, 150))
            return fillet_line_line(line1, line2, radius=15.0)

        result = benchmark(run_fillet)
        assert result is not None
        # Baseline: ~20-100 microseconds per fillet

    @pytest.mark.benchmark
    def test_point_creation_baseline(self, benchmark):
        """Baseline: Point object creation."""

        def create_points():
            p1 = Point(10, 20)
            p2 = Point(30, 40)
            return (p1, p2)

        result = benchmark(create_points)
        assert result is not None
        # Baseline: ~1-5 microseconds per operation

    @pytest.mark.benchmark
    def test_batch_line_creation_baseline(self, benchmark):
        """Baseline: Batch creation of 100 lines."""

        def create_batch():
            lines = []
            for i in range(100):
                lines.append(Line(Point(i, 0), Point(i, 100)))
            return lines

        result = benchmark(create_batch)
        assert len(result) == 100
        # Baseline: ~100-500 microseconds per 100 lines

    @pytest.mark.benchmark
    def test_batch_fillet_baseline(self, benchmark):
        """Baseline: Batch fillet operations (10 fillets)."""

        def run_batch():
            results = []
            for i in range(10):
                line1 = Line(Point(i * 10, 0), Point(i * 10 + 100, 0))
                line2 = Line(Point(i * 10 + 100, 0), Point(i * 10 + 100, 100))
                results.append(fillet_line_line(line1, line2, radius=10.0))
            return results

        result = benchmark(run_batch)
        assert len(result) == 10
        # Baseline: ~200-1000 microseconds per 10 fillets


# Performance regression thresholds (percentages)
PERFORMANCE_THRESHOLDS = {
    "line_creation": 1.5,  # 50% slower triggers warning
    "fillet_operation": 2.0,  # 100% slower triggers warning
    "point_creation": 1.5,
    "batch_operations": 2.0,
}
