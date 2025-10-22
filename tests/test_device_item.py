"""Non-GUI unit tests for `DeviceItem` that don't require showing windows.

These tests construct `DeviceItem` objects and verify serialization and
basic property setters. They will be skipped if PySide6 or `DeviceItem` is not
importable in the current environment.
"""

import pytest


def test_device_item_basic_properties_or_skip():
    try:
        from PySide6 import QtWidgets

        from frontend.device import DeviceItem
    except Exception:
        pytest.skip("PySide6 or DeviceItem not available in this environment")

    # Create a QApplication instance if none exists (safe in tests)
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])

    device = DeviceItem(10, 20, "SD", "Smoke Detector", "Test Mfg", "PN-123")

    # Basic fields
    assert device.symbol == "SD"
    assert device.name == "Smoke Detector"
    assert device.manufacturer == "Test Mfg"
    assert device.part_number == "PN-123"

    # Test serialization round-trip
    j = device.to_json()
    assert j["symbol"] == "SD"
    assert float(j["x"]) == pytest.approx(10)

    new = DeviceItem.from_json(j)
    assert new.name == device.name

    # Test label offset setter doesn't raise
    device.set_label_offset(5, 6)

    # Test coverage API (no exceptions)
    device.set_coverage({"mode": "none", "computed_radius_ft": 0})
