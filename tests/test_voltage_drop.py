from cad_core.calculations.voltage_drop import total_voltage_drop, voltage_drop_segment


def test_voltage_drop_segment_basic():
    assert voltage_drop_segment(2.0, 5.0) == 10.0


def test_total_voltage_drop_multiple_segments():
    segs = [(2.0, 5.0), (1.5, 2.0), (0.5, 10.0)]
    # drops: 10, 3, 5 -> total 18
    assert total_voltage_drop(segs) == 18.0


def test_total_voltage_drop_empty():
    assert total_voltage_drop([]) == 0.0
