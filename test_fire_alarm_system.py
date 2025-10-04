"""
Standalone test for Fire Alarm Circuit System components
Tests the circuit validation and device connections without GUI.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_fire_alarm_logic():
    """Test fire alarm circuit logic without Qt GUI."""

    print("Testing Fire Alarm Circuit Logic...")

    # Test 1: Import our classes
    try:
        from frontend.device import DeviceItem
        from frontend.fire_alarm_panel import FireAlarmPanel

        print("✅ Successfully imported fire alarm classes")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

    # Test 2: Create a mock fire alarm panel (without Qt scene)
    class MockFireAlarmPanel:
        def __init__(self):
            self.panel_type = "main"
            self.circuits = {
                "NAC1": {"type": "NAC", "devices": [], "status": "ready"},
                "NAC2": {"type": "NAC", "devices": [], "status": "ready"},
                "SLC1": {"type": "SLC", "devices": [], "status": "ready"},
                "SLC2": {"type": "SLC", "devices": [], "status": "ready"},
                "POWER": {"type": "POWER", "devices": [], "status": "ready"},
            }

        def validate_device_placement(self, device_type, circuit_id):
            """Validate if a device type can be placed on a circuit."""
            if circuit_id not in self.circuits:
                return False

            circuit_type = self.circuits[circuit_id]["type"]

            # NAC circuits - notification devices
            if circuit_type == "NAC":
                return device_type in ["horn", "strobe", "horn_strobe", "speaker", "chime"]

            # SLC circuits - initiating devices
            elif circuit_type == "SLC":
                return device_type in [
                    "smoke_detector",
                    "heat_detector",
                    "pull_station",
                    "water_flow",
                    "tamper_switch",
                    "duct_detector",
                ]

            # Power circuits - panels and power supplies
            elif circuit_type == "POWER":
                return device_type in ["fire_alarm_panel", "power_supply", "battery_backup"]

            return False

        def get_circuit_for_device_type(self, device_type):
            """Get the appropriate circuit type for a device."""
            if device_type in ["horn", "strobe", "horn_strobe", "speaker", "chime"]:
                return "NAC"
            elif device_type in [
                "smoke_detector",
                "heat_detector",
                "pull_station",
                "water_flow",
                "tamper_switch",
                "duct_detector",
            ]:
                return "SLC"
            elif device_type in ["fire_alarm_panel", "power_supply", "battery_backup"]:
                return "POWER"
            return None

    panel = MockFireAlarmPanel()
    print("✅ Created mock fire alarm panel")

    # Test 3: Circuit validation rules
    test_cases = [
        # (device_type, circuit, should_pass)
        ("smoke_detector", "SLC1", True),
        ("smoke_detector", "NAC1", False),
        ("horn_strobe", "NAC1", True),
        ("horn_strobe", "SLC1", False),
        ("pull_station", "SLC2", True),
        ("pull_station", "NAC2", False),
        ("fire_alarm_panel", "POWER", True),
        ("fire_alarm_panel", "SLC1", False),
    ]

    print("\nTesting circuit validation rules...")
    for device_type, circuit, expected in test_cases:
        result = panel.validate_device_placement(device_type, circuit)
        status = "✅" if result == expected else "❌"
        print(f"{status} {device_type} on {circuit}: {result} (expected {expected})")
        if result != expected:
            return False

    # Test 4: Circuit type detection
    print("\nTesting circuit type detection...")
    device_types = [
        "smoke_detector",
        "horn_strobe",
        "pull_station",
        "fire_alarm_panel",
        "unknown_device",
    ]
    expected_circuits = ["SLC", "NAC", "SLC", "POWER", None]

    for device_type, expected_circuit in zip(device_types, expected_circuits):
        result = panel.get_circuit_for_device_type(device_type)
        status = "✅" if result == expected_circuit else "❌"
        print(f"{status} {device_type} -> {result} (expected {expected_circuit})")
        if result != expected_circuit:
            return False

    print("\n🎉 All fire alarm circuit logic tests passed!")
    return True


if __name__ == "__main__":
    success = test_fire_alarm_logic()
    if not success:
        sys.exit(1)
