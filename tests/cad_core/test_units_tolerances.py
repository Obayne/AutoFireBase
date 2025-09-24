import math

from cad_core.units import EPS, almost_equal, clamp, sgn, round_tol


def test_eps_value_and_usage():
    assert isinstance(EPS, float)
    assert EPS == 1e-9
    # Values within EPS are considered equal
    assert almost_equal(1.0, 1.0 + EPS * 0.5)


def test_almost_equal_with_custom_tol():
    assert almost_equal(0.0, 1e-6, tol=1e-5)
    assert not almost_equal(0.0, 2e-5, tol=1e-5)


def test_clamp_basic_and_swapped_bounds():
    assert clamp(5.0, 0.0, 10.0) == 5.0
    assert clamp(-1.0, 0.0, 10.0) == 0.0
    assert clamp(11.0, 0.0, 10.0) == 10.0
    # Swapped bounds should be handled
    assert clamp(5.0, 10.0, 0.0) == 5.0


def test_sgn_with_tolerance():
    assert sgn(1.0) == 1
    assert sgn(-1.0) == -1
    assert sgn(EPS * 0.5) == 0
    assert sgn(-EPS * 0.5) == 0


def test_round_tol_behaviour():
    assert round_tol(1.2345, 0.01) == 1.23
    assert round_tol(-1.234, 0.1) == -1.2
    # Non-positive tolerance returns the input as-is
    x = 3.14159
    assert round_tol(x, 0.0) == x
    assert round_tol(x, -0.1) == x

