from __future__ import annotations

from cad_core.conduit_fill import awg_area_in2, compute_fill_pct


def test_awg_area_basic():
    # 18 AWG area should be smaller than 12 AWG
    a18 = awg_area_in2(18)
    a12 = awg_area_in2(12)
    assert a18 < a12


def test_conduit_fill_under_limit():
    # Ten 18 AWG conductors in 3/4" EMT should be well under 40%
    pct, ok = compute_fill_pct("EMT", "3/4", {18: 10})
    assert ok is True
    assert 0.0 < pct < 40.0


def test_conduit_fill_over_limit():
    # A contrived overfill: many 10 AWG in 1/2" EMT should exceed 40%
    pct, ok = compute_fill_pct("EMT", "1/2", {10: 50})
    assert ok is False
    assert pct > 40.0
