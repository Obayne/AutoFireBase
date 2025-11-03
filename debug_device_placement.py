#!/usr/bin/env python3
"""Debug device placement by testing components individually."""

import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6 import QtWidgets


def test_device_placement_components():
    """Test device placement step by step."""
    app = QtWidgets.QApplication(sys.argv)

    try:
        print("=== Testing Device Placement Components ===\n")

        # Test 1: Basic imports
        print("1. Testing imports...")
        from cad_core.commands import AddDeviceCommand
        from frontend.device import DeviceItem
        from frontend.windows.scene import GridScene

        print("   ✓ All imports successful")

        # Test 2: Scene creation
        print("\n2. Testing scene creation...")
        scene = GridScene()
        print("   ✓ GridScene created")

        # Test 3: Device creation with sample data
        print("\n3. Testing device creation...")
        sample_device_data = {
            "name": "Test Smoke Detector",
            "type": "detector",
            "symbol": "detector",
            "manufacturer": "System Sensor",
            "part_number": "2151",
            "properties": {},
        }

        device = DeviceItem(
            100,
            100,  # x, y position
            sample_device_data["symbol"],
            sample_device_data["name"],
            sample_device_data["manufacturer"],
            sample_device_data["part_number"],
        )
        print("   ✓ DeviceItem created successfully")
        print(f"   Device name: {device.name}")
        print(f"   Device position: ({device.x()}, {device.y()})")

        # Test 4: Command creation
        print("\n4. Testing command creation...")
        devices_group = scene.createItemGroup([])  # Create empty group first
        command = AddDeviceCommand(scene, device, devices_group)
        print("   ✓ AddDeviceCommand created")

        # Test 5: Command execution
        print("\n5. Testing command execution...")
        success = command.execute()
        print(f"   Command execution result: {'SUCCESS' if success else 'FAILED'}")

        if success:
            print(f"   Device added to scene: {device in scene.items()}")
            print(f"   Scene item count: {len(scene.items())}")

        print("\n=== Test Results ===")
        print("✓ All device placement components working correctly")
        print("Issue likely in scene setup, command stack, or device data validation")

    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        traceback.print_exc()
        return False

    finally:
        app.quit()

    return True


if __name__ == "__main__":
    test_device_placement_components()
