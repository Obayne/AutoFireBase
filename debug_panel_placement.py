"""
Debug Fire Alarm Panel Placement
Test what happens when trying to place a fire alarm panel.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def debug_panel_placement():
    """
    Debug Fire Alarm Panel Placement
    Test what happens when trying to place a fire alarm panel.

    This script is a small helper for developers to exercise the panel
    creation code path outside of the full GUI. It's not imported by the
    application at runtime and is intended to be run manually.
    """

    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    def debug_panel_placement():
        """Debug the panel placement process."""

        print("Debugging Fire Alarm Panel Placement...")

        # Load the catalog to get the fire alarm panel device
        from backend.catalog import load_catalog

        devices = load_catalog()

        panel_device = None
        for device in devices:
            if device.get("type", "").lower() == "panel":
                panel_device = device
                break

        if not panel_device:
            print("❌ No fire alarm panel found in catalog")
            return False

        print(f"✅ Found panel device: {panel_device}")
        print(f"  Name: {panel_device.get('name')}")
        print(f"  Type: {panel_device.get('type')}")
        print(f"  Symbol: {panel_device.get('symbol')}")
        print(f"  Manufacturer: {panel_device.get('manufacturer')}")
        print(f"  Part Number: {panel_device.get('part_number')}")

        # Test the device type check logic
        device_type = panel_device.get("type", "other").lower()
        print(f"\nDevice type check: '{device_type}'")

        should_be_panel = device_type in ["panel", "fire_alarm_panel", "main_panel"]
        print(f"Should create FireAlarmPanel: {should_be_panel}")

        if should_be_panel:
            print("✅ Device type detection working correctly")
        else:
            print("❌ Device type detection failed")
            return False

        # Test creating the FireAlarmPanel
        try:
            from PySide6.QtWidgets import QApplication

            _app = QApplication.instance() or QApplication(sys.argv)

            from frontend.fire_alarm_panel import FireAlarmPanel

            device_name = (
                panel_device.get("name")
                or panel_device.get("model")
                or panel_device.get("device_type")
                or "Unknown"
            )

            device_symbol = panel_device.get("symbol") or panel_device.get("uid") or "?"

            print("\nCreating FireAlarmPanel:")
            print("  Position: (100, 100)")
            print(f"  Symbol: '{device_symbol}'")
            print(f"  Name: '{device_name}'")
            print(f"  Manufacturer: '{panel_device.get('manufacturer', '')}'")
            print(f"  Part Number: '{panel_device.get('part_number', '')}'")

            # This should work now with the fixed constructor
            panel = FireAlarmPanel(
                100,
                100,
                device_symbol,
                device_name,
                panel_device.get("manufacturer", ""),
                panel_device.get("part_number", ""),
            )
            panel.panel_type = "main"
            panel.device_type = "fire_alarm_panel"

            print("✅ FireAlarmPanel created successfully!")
            print(f"  Panel name: {panel.name}")
            print(f"  Panel type: {panel.panel_type}")
            print(f"  Device type: {panel.device_type}")
            print(f"  Symbol: {panel.symbol}")
            print(f"  Circuits: {list(panel.circuits.keys())}")

            return True

        except Exception as e:
            print(f"❌ Error creating FireAlarmPanel: {e}")
            import traceback

            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = debug_panel_placement()
        if success:
            print("\n🎉 Fire Alarm Panel placement debug completed successfully!")
            print("\nIf the panel is still ghosted in the app, the issue might be:")
            print("1. The command stack execution failing")
            print("2. The ghost device not being removed after placement")
            print("3. Event handling issues in the scene")
        else:
            sys.exit(1)
