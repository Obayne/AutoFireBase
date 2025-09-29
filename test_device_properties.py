#!/usr/bin/env python3
"""
Test script for enhanced DeviceItem electrical properties.
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))


def test_device_electrical_properties():
    """Test device electrical properties without GUI."""
    print("Testing DeviceItem Electrical Properties")
    print("=" * 40)

    # Import DeviceItem (avoid GUI components)
    try:
        from device import DeviceItem

        # Create a device without GUI
        device = DeviceItem.__new__(DeviceItem)  # Create without __init__ to avoid GUI
        device.name = "Smoke Detector"
        device.symbol = "SD"

        # Initialize electrical properties manually
        device.electrical = {
            "terminals": [],
            "current_standby_a": 0.02,
            "current_alarm_a": 0.15,
            "voltage_v": 24.0,
            "power_w": 0.0,
            "wire_gauge": 18,
            "connection_type": "screw",
        }

        # Test terminal initialization
        device._init_terminals()

        print(f"Device: {device.name}")
        print(f"Symbol: {device.symbol}")
        print(f"Standby Current: {device.electrical['current_standby_a']}A")
        print(f"Alarm Current: {device.electrical['current_alarm_a']}A")
        print(f"Operating Voltage: {device.electrical['voltage_v']}V")
        print(f"Terminals: {len(device.electrical['terminals'])}")

        for terminal in device.electrical["terminals"]:
            print(f"  - {terminal['name']}: {terminal['type']} at {terminal['pos']}")

        # Test serialization
        json_data = device.to_json()
        print(f"\nSerialized electrical properties: {json_data.get('electrical', {})}")

        print("\nDevice electrical properties test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_device_electrical_properties()
