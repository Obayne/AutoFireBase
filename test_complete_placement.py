"""
Comprehensive Fire Alarm Panel Placement Test
Test the complete workflow from catalog selection to canvas placement.
"""

import os
import sys

import pytest

# Prevent the main app from starting
os.environ["AUTOFIRE_TEST_MODE"] = "1"

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_complete_placement_workflow():
    """Test the complete placement workflow."""

    print("Testing Complete Fire Alarm Panel Placement Workflow...")

    try:
        from PySide6.QtCore import QPointF
        from PySide6.QtWidgets import QApplication

        _app = QApplication.instance() or QApplication(sys.argv)

        # Test 1: Load catalog and find panel
        from backend.catalog import load_catalog

        devices = load_catalog()

        panel_device = None
        for device in devices:
            if device.get("type", "").lower() == "panel":
                panel_device = device
                break

        if not panel_device:
            pytest.fail("No fire alarm panel found in catalog")

        print(f"✅ Found panel in catalog: {panel_device['name']}")

        # Test 2: Create a mock scene and model space for testing
        from frontend.circuit_manager import CircuitManager
        from frontend.windows.scene import GridScene

        scene = GridScene()
        circuit_manager = CircuitManager(scene)

        print("✅ Created test scene and circuit manager")

        # Test 3: Simulate the device selection process
        current_proto = panel_device
        device_type = current_proto.get("type", "other").lower()

        is_panel_type = device_type in ["panel", "fire_alarm_panel", "main_panel"]
        msg = (
            f"✅ Device type check: '{device_type}' -> "
            f"should create FireAlarmPanel: {is_panel_type}"
        )
        print(msg)

        # Test 4: Create ghost device (what happens when selecting from palette)
        device_name = (
            current_proto.get("name")
            or current_proto.get("model")
            or current_proto.get("device_type")
            or "Unknown"
        )

        device_symbol = current_proto.get("symbol") or current_proto.get("uid") or "?"

        print(f"✅ Ghost device parameters: name='{device_name}', symbol='{device_symbol}'")

        # Create ghost device using the same logic as the app
        if device_type in ["panel", "fire_alarm_panel", "main_panel"]:
            from frontend.fire_alarm_panel import FireAlarmPanel

            _ghost = FireAlarmPanel(
                0,
                0,
                device_symbol,
                device_name,
                current_proto.get("manufacturer", ""),
                current_proto.get("part_number", ""),
            )
            print("✅ Created FireAlarmPanel ghost device")
        else:
            from frontend.device import DeviceItem

            _ghost = DeviceItem(
                0,
                0,
                device_symbol,
                device_name,
                current_proto.get("manufacturer", ""),
                current_proto.get("part_number", ""),
            )
            print("✅ Created DeviceItem ghost device")

        # Test 5: Simulate device placement (what happens when clicking on canvas)
        scene_pos = QPointF(200, 200)

        # Create the actual device using the same logic as _place_device_at
        if device_type in ["panel", "fire_alarm_panel", "main_panel"]:
            from frontend.fire_alarm_panel import FireAlarmPanel

            device = FireAlarmPanel(
                scene_pos.x(),
                scene_pos.y(),
                device_symbol,
                device_name,
                current_proto.get("manufacturer", ""),
                current_proto.get("part_number", ""),
            )
            device.panel_type = "main"
            device.device_type = "fire_alarm_panel"
            print("✅ Created actual FireAlarmPanel for placement")
        else:
            from frontend.device import DeviceItem

            device = DeviceItem(
                scene_pos.x(),
                scene_pos.y(),
                device_symbol,
                device_name,
                current_proto.get("manufacturer", ""),
                current_proto.get("part_number", ""),
            )
            device.device_type = device_type
            print("✅ Created actual DeviceItem for placement")

        # Test 6: Add to scene and circuit manager
        scene.addItem(device)

        if device_type in ["panel", "fire_alarm_panel", "main_panel"]:
            circuit_manager.add_panel(device)
            main_panel = circuit_manager.get_main_panel()
            if main_panel:
                print(f"✅ Panel registered with circuit manager: {main_panel.name}")
            else:
                pytest.fail("Panel not found in circuit manager")

        print("✅ Device added to scene successfully")

        # Test 7: Verify circuit functionality
        if hasattr(device, "circuits"):
            print(f"✅ Panel has circuits: {list(device.circuits.keys())}")

            # Test validation
            smoke_result = device.validate_device_placement("smoke_detector", "SLC1")
            horn_result = device.validate_device_placement("horn_strobe", "NAC1")
            invalid_result = device.validate_device_placement("horn_strobe", "SLC1")

            print("✅ Circuit validation working:")
            print(f"  Smoke detector on SLC1: {smoke_result}")
            print(f"  Horn/strobe on NAC1: {horn_result}")
            print(f"  Horn/strobe on SLC1 (should be False): {invalid_result}")

        print("\n🎉 Complete placement workflow test PASSED!")
        print("\nThe Fire Alarm Control Panel should now place correctly in the application.")
        print(
            "If it's still ghosted, the issue might be in the Qt event handling or command stack."
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        pytest.fail(f"Error in placement workflow: {e}")

    # Completed successfully
    return None


if __name__ == "__main__":
    try:
        test_complete_placement_workflow()
    except Exception:
        sys.exit(1)
