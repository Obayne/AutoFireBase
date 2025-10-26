from backend.circuits import estimate_device_currents


class Device:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_lookup_by_part_number_from_json():
    d = Device(name="Horn/Strobe", part_number="P2R")
    s, a = estimate_device_currents(d)
    # From backend/device_currents.json: 0.158 A alarm
    assert s >= 0.0
    assert 0.150 <= a <= 0.170


def test_lookup_precedes_heuristics():
    # Even if name suggests a different heuristic, JSON should win when matching model
    d = Device(name="Random Device", model="SD-355")
    s, a = estimate_device_currents(d)
    # From JSON: ~0.000085 A
    assert 0.0 <= s <= 0.001
    assert 0.0 <= a <= 0.001


def test_keyword_fallback_when_unknown():
    d = Device(name="Turbo Horn", part_number="HS-UNKNOWN")
    s, a = estimate_device_currents(d)
    # Heuristic horn current ~0.09 A alarm
    assert s == 0.0 or s < 0.02
    assert 0.05 <= a <= 0.15
