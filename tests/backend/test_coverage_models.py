import math

import pytest

from backend.coverage_models import db_at_distance, radius_for_target_db


def test_db_at_distance_reference_match():
    # At reference distance, level should match reference level
    assert db_at_distance(90.0, r_ref_ft=10.0, r_ft=10.0) == pytest.approx(90.0)


def test_db_at_distance_inverse_square_drop():
    # Doubling distance should drop ~6.0206 dB
    l10 = db_at_distance(90.0, r_ref_ft=10.0, r_ft=10.0)
    l20 = db_at_distance(90.0, r_ref_ft=10.0, r_ft=20.0)
    assert (l10 - l20) == pytest.approx(20 * math.log10(2.0))


def test_radius_for_target_db_solve_exact_at_reference():
    # If target equals reference level, radius == reference distance
    r = radius_for_target_db(90.0, target_db=90.0, r_ref_ft=10.0)
    assert r == pytest.approx(10.0)


def test_radius_for_target_db_plus6db_uses_exact_inverse_square():
    # +6 dB target relative to ref → factor 10**(-6/20)
    expected = 10.0 * (10 ** ((90.0 - 96.0) / 20.0))
    r = radius_for_target_db(90.0, target_db=96.0, r_ref_ft=10.0)
    assert r == pytest.approx(expected, rel=1e-6)


def test_radius_for_target_db_minus6db_uses_exact_inverse_square():
    # -6 dB target relative to ref → factor 10**(+6/20)
    expected = 10.0 * (10 ** ((90.0 - 84.0) / 20.0))
    r = radius_for_target_db(90.0, target_db=84.0, r_ref_ft=10.0)
    assert r == pytest.approx(expected, rel=1e-6)


def test_radius_for_target_db_clamps():
    # Very high target should clamp to min; very low to max
    r_min = radius_for_target_db(
        90.0, target_db=150.0, r_ref_ft=10.0, min_radius_ft=0.5, max_radius_ft=100.0
    )
    r_max = radius_for_target_db(
        90.0, target_db=10.0, r_ref_ft=10.0, min_radius_ft=0.5, max_radius_ft=100.0
    )
    assert r_min == 0.5
    assert r_max == 100.0


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        db_at_distance(90.0, r_ref_ft=0.0, r_ft=10.0)
    with pytest.raises(ValueError):
        db_at_distance(90.0, r_ref_ft=10.0, r_ft=0.0)
    with pytest.raises(ValueError):
        radius_for_target_db(90.0, 80.0, r_ref_ft=0.0)
    with pytest.raises(ValueError):
        radius_for_target_db(90.0, 80.0, r_ref_ft=10.0, min_radius_ft=-1, max_radius_ft=1)
