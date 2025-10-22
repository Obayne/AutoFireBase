import pytest


@pytest.mark.gui
def test_device_placement_gui(skip_if_no_qt, qapp):
    """GUI smoke test for device placement behavior using DeviceItem."""
    try:
        from frontend.device import DeviceItem
    except Exception:
        pytest.skip("DeviceItem not available; skipping")

    # construct item and verify position and movement
    device = DeviceItem(100, 150, "SD", "Smoke Detector", "Test Mfg", "PN-001")
    pos = device.pos()
    assert pos.x() == pytest.approx(100)
    assert pos.y() == pytest.approx(150)

    # move device
    device.setPos(200, 250)
    pos2 = device.pos()
    assert pos2.x() == pytest.approx(200)
    assert pos2.y() == pytest.approx(250)
