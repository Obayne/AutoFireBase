"""Parity test for fillet wrappers.

Skips if legacy cad_core.fillet is not importable.
"""

from __future__ import annotations

import pytest

from lv_cad.operations.fillet import fillet_line_line

try:
    from cad_core.fillet import fillet_line_line as legacy_fillet_line_line  # type: ignore
except ImportError:
    legacy_fillet_line_line = None


def _simple_lines():
    # Minimal synthetic perpendicular lines sharing a pick point
    # Legacy fillet expects two Line objects; import them if available.
    try:
        from cad_core.lines import Line, Point  # type: ignore
    except ImportError:
        pytest.skip("Legacy Line/Point types not available for parity test")

    p0 = Point(0.0, 0.0)
    p1 = Point(10.0, 0.0)
    p2 = Point(0.0, 10.0)
    l1 = Line(p0, p1)
    l2 = Line(p0, p2)
    return l1, l2


@pytest.mark.skipif(legacy_fillet_line_line is None, reason="legacy fillet not importable")
def test_fillet_line_line_parity():
    if legacy_fillet_line_line is None:
        pytest.skip("legacy fillet not importable")
    l1, l2 = _simple_lines()
    r = 2.0
    new = fillet_line_line(l1, l2, r)
    legacy = legacy_fillet_line_line(l1, l2, r)
    # Both None (if no fillet) or both tuples of Points. Basic structural parity.
    assert (new is None and legacy is None) or (new is not None and legacy is not None)
    if new and legacy:
        # Compare coordinates with rounding tolerance
        from collections.abc import Sequence as _Seq  # local import to avoid broad dependencies

        def pts(t: _Seq):  # legacy returns tuple[Point,Point,Point]
            return [(round(p.x, 6), round(p.y, 6)) for p in t]

        assert pts(new) == pts(legacy)
