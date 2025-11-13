"""Perf smoke test for fillet (optional).

Runs only when RUN_PERF=1 and legacy cad_core.fillet is available.
Prints simple timing; does not enforce thresholds.
"""

from __future__ import annotations

import os
import time

import pytest

try:
    from cad_core.fillet import fillet_line_line as legacy_fillet_line_line  # type: ignore
    from cad_core.lines import Line, Point  # type: ignore
except ImportError:  # pragma: no cover - optional legacy path
    Line = None  # type: ignore
    Point = None  # type: ignore
    legacy_fillet_line_line = None  # type: ignore


RUN_PERF = os.environ.get("RUN_PERF") == "1"


@pytest.mark.skipif(not RUN_PERF, reason="perf tests disabled (set RUN_PERF=1)")
@pytest.mark.skipif(
    legacy_fillet_line_line is None or Line is None or Point is None,
    reason="legacy fillet unavailable",
)
def test_perf_fillet_line_line_basic():
    # Simple perpendicular lines sharing origin
    l1 = Line(Point(-100.0, 0.0), Point(100.0, 0.0))
    l2 = Line(Point(0.0, -100.0), Point(0.0, 100.0))
    r = 5.0

    # Warm-up
    for _ in range(50):
        legacy_fillet_line_line(l1, l2, r)

    n = 5000
    t0 = time.perf_counter()
    for _ in range(n):
        legacy_fillet_line_line(l1, l2, r)
    dt = time.perf_counter() - t0

    # Emit basic throughput info for manual inspection
    print(f"fillet_line_line: {n} iters in {dt:.4f}s -> {n/dt:.0f} ops/s")

    # Always pass; this is a smoke/perf sampler
    assert True
