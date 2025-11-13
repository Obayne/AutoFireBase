"""Perf smoke test for offset (optional).

Runs only when RUN_PERF=1 and legacy offset is available.
Prints simple timing; does not enforce thresholds.
"""

from __future__ import annotations

import os
import time

import pytest

from lv_cad.geometry.point import Point
from lv_cad.operations import offset as _offset_mod

RUN_PERF = os.environ.get("RUN_PERF") == "1"


@pytest.mark.skipif(not RUN_PERF, reason="perf tests disabled (set RUN_PERF=1)")
def test_perf_offset_polyline_basic():
    if _offset_mod._try_legacy() is None:  # type: ignore[attr-defined]
        pytest.skip("legacy offset unavailable")

    # Simple rectangle polyline
    rect = [
        Point(0.0, 0.0),
        Point(100.0, 0.0),
        Point(100.0, 100.0),
        Point(0.0, 100.0),
        Point(0.0, 0.0),
    ]

    # Warm-up
    for _ in range(50):
        _offset_mod.offset_polyline(rect, 5.0)

    n = 2000
    t0 = time.perf_counter()
    for _ in range(n):
        _offset_mod.offset_polyline(rect, 5.0)
    dt = time.perf_counter() - t0

    print(f"offset_polyline: {n} iters in {dt:.4f}s -> {n/dt:.0f} ops/s")
    assert True
