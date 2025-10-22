import os

# Run Qt in headless mode for CI/test runners
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication

from frontend.device import DeviceItem
from frontend.fire_alarm_panel import FireAlarmPanel
from frontend.windows.scene import CanvasView, GridScene


def test_terminal_detection_and_connect():
    """Verify scene can find nearby panel terminals and devices can connect to panels."""
    app = QApplication.instance() or QApplication([])

    scene = GridScene()

    # CanvasView can accept the scene; pass None for groups and a simple window ref
    class WinRef:
        pass

    win = WinRef()
    # CanvasView stores a reference to the provided scene and exposes helper methods
    view = CanvasView(scene, None, None, None, None, win)

    # Create a panel at origin and add it to the scene
    panel = FireAlarmPanel(0, 0, symbol=None, name="TestPanel", manufacturer="TestCo")
    scene.addItem(panel)

    # Pick a known terminal (NAC1 exists in panel._terminals)
    term_item = panel._terminals.get("NAC1")
    assert term_item is not None

    # Query the canvas for nearby terminals using the terminal's scene position
    pos = term_item.scenePos()
    found_term, found_panel = view._find_nearby_terminals(QPointF(pos.x(), pos.y()), radius_px=8.0)

    assert found_term is not None
    assert found_panel is panel

    # Now create a notification device and connect it to the panel
    device = DeviceItem(10, 10, symbol="?", name="strobe", manufacturer="Acme")
    ok, msg = device.connect_to_panel(panel)
    assert ok is True
    assert device.circuit_id is not None

    app.quit()
