#!/usr/bin/env python3

from backend.catalog import load_catalog

try:
    devices = load_catalog()
    print(f"Found {len(devices)} devices in catalog:")

    for i, device in enumerate(devices[:6]):  # Show first 6
        print(f"Device {i+1}:")
        print(f"  name: {device.get('name')}")
        print(f"  symbol: {device.get('symbol')}")
        print(f"  type: {device.get('type')}")
        print(f"  manufacturer: {device.get('manufacturer')}")
        print(f"  part_number: {device.get('part_number')}")
        print()

except Exception as e:
    print(f"Error loading catalog: {e}")
    import traceback

    traceback.print_exc()
