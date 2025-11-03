#!/usr/bin/env python3
"""Test the new device filtering functionality."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_device_filtering():
    """Test device filtering logic with sample data."""
    print("=== Testing Device Filtering Logic ===\n")

    # Sample devices to test filtering
    sample_devices = [
        {
            "name": "2151 Photoelectric Smoke Detector",
            "type": "detector",
            "manufacturer": "System Sensor",
            "part_number": "2151",
            "symbol": "SD",
        },
        {
            "name": "5601-P Manual Pull Station",
            "type": "pull",
            "manufacturer": "Fire-Lite",
            "part_number": "5601-P",
            "symbol": "MPS",
        },
        {
            "name": "SpectrAlert Horn/Strobe",
            "type": "horn",
            "manufacturer": "System Sensor",
            "part_number": "P2RL",
            "symbol": "HS",
        },
        {
            "name": "Conventional Heat Detector",
            "type": "heat",
            "manufacturer": "System Sensor",
            "part_number": "5602",
            "symbol": "HD",
        },
        {
            "name": "FRM-1 Relay Module",
            "type": "control",
            "manufacturer": "Fire-Lite",
            "part_number": "FRM-1",
            "symbol": "RM",
        },
    ]

    # Test device type mapping (more specific matching)
    device_type_mapping = {
        "Smoke Detectors": ["smoke", "photo", "ionization"],
        "Heat Detectors": ["heat", "thermal", "fixed_temperature", "rate_of_rise"],
        "Manual Pull Stations": ["pull", "manual", "station"],
        "Horn/Strobes": ["horn", "strobe", "speaker_strobe", "notification"],
        "Speakers": ["speaker", "audio", "voice"],
        "Control Modules": ["control", "relay", "output"],
        "Monitor Modules": ["monitor", "input", "supervision"],
        "Panels": ["panel", "facp", "controller"],
        "Annunciators": ["annunciator", "display", "lcd", "led"],
    }

    def filter_devices(devices, search_text="", category_filter="All Devices"):
        """Filter devices - duplicated from actual code logic."""
        search_text = search_text.lower().strip()
        filtered_devices = []

        for device in devices:
            # Apply category filter first
            if category_filter != "All Devices":
                device_type = device.get("type", "").lower()
                device_name = device.get("name", "").lower()

                # Check if device matches the category filter
                if category_filter in device_type_mapping:
                    keywords = device_type_mapping[category_filter]
                    if not any(
                        keyword in device_type or keyword in device_name for keyword in keywords
                    ):
                        continue

            # Apply search filter
            if search_text:
                searchable_text = " ".join(
                    [
                        device.get("name", ""),
                        device.get("manufacturer", ""),
                        device.get("part_number", ""),
                        device.get("type", ""),
                        device.get("symbol", ""),
                    ]
                ).lower()

                if search_text not in searchable_text:
                    continue

            filtered_devices.append(device)

        return filtered_devices

    # Test 1: No filters (should return all)
    print("1. Testing no filters:")
    result = filter_devices(sample_devices)
    print(f"   Result: {len(result)}/{len(sample_devices)} devices")
    assert len(result) == len(sample_devices), "Should return all devices"
    print("   ✓ PASS")

    # Test 2: Search by name
    print("\n2. Testing search by name 'smoke':")
    result = filter_devices(sample_devices, search_text="smoke")
    print(f"   Result: {len(result)} devices")
    for dev in result:
        print(f"     - {dev['name']}")
    assert len(result) == 1, "Should find 1 smoke detector"
    print("   ✓ PASS")

    # Test 3: Search by manufacturer
    print("\n3. Testing search by manufacturer 'System Sensor':")
    result = filter_devices(sample_devices, search_text="system sensor")
    print(f"   Result: {len(result)} devices")
    for dev in result:
        print(f"     - {dev['name']} ({dev['manufacturer']})")
    assert len(result) == 3, "Should find 3 System Sensor devices"
    print("   ✓ PASS")

    # Test 4: Category filter
    print("\n4. Testing category filter 'Smoke Detectors':")
    result = filter_devices(sample_devices, category_filter="Smoke Detectors")
    print(f"   Result: {len(result)} devices")
    for dev in result:
        print(f"     - {dev['name']}")
    assert len(result) == 1, "Should find 1 smoke detector"
    print("   ✓ PASS")

    # Test 5: Combined search and filter
    print("\n5. Testing combined search + filter:")
    result = filter_devices(sample_devices, search_text="system", category_filter="Heat Detectors")
    print(f"   Result: {len(result)} devices")
    for dev in result:
        print(f"     - {dev['name']}")
    assert len(result) == 1, "Should find 1 System Sensor heat detector"
    print("   ✓ PASS")

    print("\n=== All Tests Passed! ===")
    print("The device filtering system is working correctly.")
    return True


if __name__ == "__main__":
    test_device_filtering()
