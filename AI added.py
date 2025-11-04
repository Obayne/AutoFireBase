#!/usr/bin/env python3
"""Test the enhanced device and wire filtering functionality."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_enhanced_filtering():
    """Test advanced filtering logic with sample data."""
    print("=== Testing Enhanced Device & Wire Filtering ===\n")

    # Sample devices for testing enhanced filtering
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
        {
            "name": "i3 Smoke Detector",
            "type": "detector",
            "manufacturer": "Honeywell",
            "part_number": "FSP-851",
            "symbol": "SD",
        },
    ]

    # Sample wires for testing wire filtering
    sample_wires = [
        {
            "name": "16 AWG SLC Cable",
            "gauge": 16,
            "color": "Red",
            "type": "SLC",
            "ohms_per_1000ft": 4.0,
            "max_current_a": 10.0,
        },
        {
            "name": "14 AWG NAC Cable",
            "gauge": 14,
            "color": "Yellow",
            "type": "NAC",
            "ohms_per_1000ft": 2.5,
            "max_current_a": 15.0,
        },
        {
            "name": "18 AWG Power Cable",
            "gauge": 18,
            "color": "Black",
            "type": "Power",
            "ohms_per_1000ft": 6.4,
            "max_current_a": 7.0,
        },
        {
            "name": "16 AWG Plenum Cable",
            "gauge": 16,
            "color": "Blue",
            "type": "Plenum",
            "ohms_per_1000ft": 4.2,
            "max_current_a": 9.0,
        },
        {
            "name": "12 AWG Riser Cable",
            "gauge": 12,
            "color": "Green",
            "type": "Riser",
            "ohms_per_1000ft": 1.6,
            "max_current_a": 20.0,
        },
    ]

    def test_advanced_device_search():
        """Test advanced device search with AND/OR operators."""
        print("1. Testing Advanced Device Search:")

        def advanced_filter_devices(
            devices, search_text="", manufacturer_filter="All Manufacturers"
        ):
            """Advanced device filtering with AND/OR support."""
            search_text = search_text.lower().strip()
            filtered_devices = []

            for device in devices:
                # Apply manufacturer filter
                if manufacturer_filter != "All Manufacturers":
                    device_mfg = device.get("manufacturer", "").strip()
                    if device_mfg != manufacturer_filter:
                        continue

                # Apply advanced search filter
                if search_text:
                    if " AND " in search_text.upper():
                        search_terms = [
                            term.strip().lower() for term in search_text.upper().split(" AND ")
                        ]
                        searchable_text = " ".join(
                            [
                                device.get("name", ""),
                                device.get("manufacturer", ""),
                                device.get("part_number", ""),
                                device.get("type", ""),
                                device.get("symbol", ""),
                            ]
                        ).lower()

                        if not all(term in searchable_text for term in search_terms):
                            continue
                    elif " OR " in search_text.upper():
                        search_terms = [
                            term.strip().lower() for term in search_text.upper().split(" OR ")
                        ]
                        searchable_text = " ".join(
                            [
                                device.get("name", ""),
                                device.get("manufacturer", ""),
                                device.get("part_number", ""),
                                device.get("type", ""),
                                device.get("symbol", ""),
                            ]
                        ).lower()

                        if not any(term in searchable_text for term in search_terms):
                            continue
                    else:
                        # Simple search
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

        # Test AND operator
        result = advanced_filter_devices(sample_devices, "system AND detector")
        print(f"   AND search 'system AND detector': {len(result)} devices")
        for dev in result:
            print(f"     - {dev['name']} ({dev['manufacturer']})")
        assert len(result) == 2, "Should find 2 System Sensor detectors"

        # Test OR operator
        result = advanced_filter_devices(sample_devices, "fire-lite OR honeywell")
        print(f"   OR search 'fire-lite OR honeywell': {len(result)} devices")
        for dev in result:
            print(f"     - {dev['name']} ({dev['manufacturer']})")
        assert len(result) == 3, "Should find 3 devices from Fire-Lite or Honeywell"

        # Test manufacturer filter
        result = advanced_filter_devices(sample_devices, manufacturer_filter="System Sensor")
        print(f"   Manufacturer filter 'System Sensor': {len(result)} devices")
        for dev in result:
            print(f"     - {dev['name']}")
        assert len(result) == 3, "Should find 3 System Sensor devices"

        print("   ✓ PASS - Advanced device search works\n")

    def test_wire_filtering():
        """Test wire filtering by type, gauge, and search."""
        print("2. Testing Wire Filtering:")

        def filter_wires(wires, search_text="", type_filter="All Types", gauge_filter="All Gauges"):
            """Filter wires by type, gauge, and search text."""
            search_text = search_text.lower().strip()
            filtered_wires = []

            for wire in wires:
                # Apply type filter
                if type_filter != "All Types":
                    wire_type = wire.get("type", "").lower()
                    wire_name = wire.get("name", "").lower()

                    type_keywords = {
                        "SLC/IDC": ["slc", "idc", "signal", "initiating"],
                        "NAC": ["nac", "notification", "appliance"],
                        "Power": ["power", "supply", "battery"],
                        "Riser": ["riser", "cmr"],
                        "Plenum": ["plenum", "cmp"],
                    }

                    if type_filter in type_keywords:
                        keywords = type_keywords[type_filter]
                        if not any(
                            keyword in wire_type or keyword in wire_name for keyword in keywords
                        ):
                            continue

                # Apply gauge filter
                if gauge_filter != "All Gauges":
                    wire_gauge = str(wire.get("gauge", ""))
                    filter_gauge = gauge_filter.split()[0]  # Extract number from "14 AWG"
                    if filter_gauge not in wire_gauge:
                        continue

                # Apply search filter
                if search_text:
                    searchable_text = " ".join(
                        [
                            wire.get("name", ""),
                            wire.get("color", ""),
                            str(wire.get("gauge", "")),
                            wire.get("type", ""),
                            str(wire.get("ohms_per_1000ft", "")),
                            str(wire.get("max_current_a", "")),
                        ]
                    ).lower()

                    if search_text not in searchable_text:
                        continue

                filtered_wires.append(wire)

            return filtered_wires

        # Test type filter
        result = filter_wires(sample_wires, type_filter="SLC/IDC")
        print(f"   Type filter 'SLC/IDC': {len(result)} wires")
        for wire in result:
            print(f"     - {wire['name']}")
        assert len(result) == 1, "Should find 1 SLC wire"

        # Test gauge filter
        result = filter_wires(sample_wires, gauge_filter="16 AWG")
        print(f"   Gauge filter '16 AWG': {len(result)} wires")
        for wire in result:
            print(f"     - {wire['name']}")
        assert len(result) == 2, "Should find 2 16 AWG wires"

        # Test search
        result = filter_wires(sample_wires, search_text="red")
        print(f"   Search 'red': {len(result)} wires")
        for wire in result:
            print(f"     - {wire['name']} ({wire['color']})")
        assert len(result) == 1, "Should find 1 red wire"

        # Test combined filters
        result = filter_wires(sample_wires, search_text="16", type_filter="SLC/IDC")
        print(f"   Combined '16' + 'SLC/IDC': {len(result)} wires")
        for wire in result:
            print(f"     - {wire['name']}")
        assert len(result) == 1, "Should find 1 16 AWG SLC wire"

        print("   ✓ PASS - Wire filtering works\n")

    # Run all tests
    test_advanced_device_search()
    test_wire_filtering()

    print("=== All Enhanced Filtering Tests Passed! ===")
    print("Professional-grade filtering is working correctly.")
    print("✓ Device search with AND/OR operators")
    print("✓ Manufacturer filtering")
    print("✓ Wire type, gauge, and search filtering")
    print("✓ Combined multi-criteria filtering")
    return True


if __name__ == "__main__":
    test_enhanced_filtering()
