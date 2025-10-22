import pytest

from cad_core.calculations.battery_sizing import required_ah


def test_required_ah_basic():
    # two devices at 1A each, 4 hours backup, 80% derate -> AH = (2 * 4)/0.8 = 10
    assert pytest.approx(required_ah([1.0, 1.0], 4.0, 0.8), rel=1e-6) == 10.0


def test_required_ah_zero_hours():
    with pytest.raises(ValueError):
        required_ah([0.5], 0)


def test_required_ah_derate_bounds():
    with pytest.raises(ValueError):
        required_ah([1.0], 2.0, derate=0)
    with pytest.raises(ValueError):
        required_ah([1.0], 2.0, derate=1.5)
