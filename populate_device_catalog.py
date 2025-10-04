#!/usr/bin/env python3
"""
Populate the AutoFire database with a comprehensive device catalog
for testing the System Builder.
"""

import json
import sqlite3


def populate_devices():
    """Add more devices to the database for better System Builder testing."""

    conn = sqlite3.connect("autofire.db")
    cursor = conn.cursor()

    # Additional devices to add
    new_devices = [
        # More detectors
        {
            "manufacturer": "System Sensor",
            "type": "Detector",
            "model": "2WT-B",
            "name": "Photoelectric Smoke Detector",
            "symbol": "SD",
        },
        {
            "manufacturer": "System Sensor",
            "type": "Detector",
            "model": "5602",
            "name": "Fixed Temperature Heat Detector",
            "symbol": "HD",
        },
        {
            "manufacturer": "Honeywell",
            "type": "Detector",
            "model": "SD365",
            "name": "Ionization Smoke Detector",
            "symbol": "SD",
        },
        {
            "manufacturer": "Honeywell",
            "type": "Detector",
            "model": "HD135F",
            "name": "Rate-of-Rise Heat Detector",
            "symbol": "HD",
        },
        # More notification devices
        {
            "manufacturer": "System Sensor",
            "type": "Notification",
            "model": "P2R",
            "name": "Red Horn Strobe",
            "symbol": "HS",
        },
        {
            "manufacturer": "System Sensor",
            "type": "Notification",
            "model": "P2W",
            "name": "White Horn Strobe",
            "symbol": "HS",
        },
        {
            "manufacturer": "Wheelock",
            "type": "Notification",
            "model": "AS-24MCW",
            "name": "Ceiling Mount Speaker Strobe",
            "symbol": "SS",
        },
        {
            "manufacturer": "Wheelock",
            "type": "Notification",
            "model": "NS-24MCW",
            "name": "Wall Mount Speaker Strobe",
            "symbol": "SS",
        },
        {
            "manufacturer": "Simplex",
            "type": "Notification",
            "model": "4906-9356",
            "name": "High Candela Strobe",
            "symbol": "S",
        },
        # Pull stations
        {
            "manufacturer": "Fire-Lite",
            "type": "Initiating",
            "model": "BG-12",
            "name": "Single Action Pull Station",
            "symbol": "PS",
        },
        {
            "manufacturer": "Honeywell",
            "type": "Initiating",
            "model": "PS-6",
            "name": "Dual Action Pull Station",
            "symbol": "PS",
        },
        # More panels
        {
            "manufacturer": "Fire-Lite",
            "type": "Panel",
            "model": "NFS2-640",
            "name": "Intelligent Fire Alarm Control Panel",
            "symbol": "FACP",
        },
        {
            "manufacturer": "Simplex",
            "type": "Panel",
            "model": "4100ES",
            "name": "Essential Fire Alarm Control Panel",
            "symbol": "FACP",
        },
        # Special detectors
        {
            "manufacturer": "VESDA",
            "type": "Detector",
            "model": "VLS-500",
            "name": "Very Early Smoke Detection Aspirating",
            "symbol": "ASD",
        },
        {
            "manufacturer": "Det-Tronics",
            "type": "Detector",
            "model": "X3302",
            "name": "UV/IR Flame Detector",
            "symbol": "FD",
        },
    ]

    # Get manufacturer IDs and type IDs
    cursor.execute("SELECT id, name FROM manufacturers")
    manufacturers = {row[1]: row[0] for row in cursor.fetchall()}

    cursor.execute("SELECT id, code FROM device_types")
    device_types = {row[1]: row[0] for row in cursor.fetchall()}

    # Add missing manufacturers
    new_manufacturers = ["System Sensor", "Wheelock", "Simplex", "VESDA", "Det-Tronics"]
    for mfg in new_manufacturers:
        if mfg not in manufacturers:
            cursor.execute("INSERT INTO manufacturers (name) VALUES (?)", (mfg,))
            manufacturers[mfg] = cursor.lastrowid

    # Add missing device types
    new_types = [
        ("Initiating", "Pull Stations and Manual Devices"),
        ("Panel", "Fire Alarm Control Panels"),
    ]
    for type_code, description in new_types:
        if type_code not in device_types:
            cursor.execute(
                "INSERT INTO device_types (code, description) VALUES (?, ?)",
                (type_code, description),
            )
            device_types[type_code] = cursor.lastrowid

    # Add devices
    added_count = 0
    for device in new_devices:
        # Check if device already exists
        cursor.execute(
            """
            SELECT COUNT(*) FROM devices
            WHERE model = ? AND manufacturer_id = ?
        """,
            (device["model"], manufacturers.get(device["manufacturer"], 1)),
        )

        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO devices (manufacturer_id, type_id, model, name, symbol, properties_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    manufacturers.get(device["manufacturer"], 1),
                    device_types.get(device["type"], 1),
                    device["model"],
                    device["name"],
                    device["symbol"],
                    "{}",
                ),
            )
            added_count += 1

    # Add more panels to the panels table
    new_panels = [
        {
            "manufacturer": "Fire-Lite",
            "model": "NFS2-640",
            "name": "NFS2-640 Intelligent Fire Alarm Control Panel",
            "panel_type": "main",
            "max_devices": 636,
            "properties": {
                "power_supply": "120/240VAC",
                "battery_capacity": "200AH",
                "communication_protocols": ["SLC", "NAC", "Ethernet"],
            },
        },
        {
            "manufacturer": "Simplex",
            "model": "4100ES",
            "name": "4100ES Essential Fire Alarm Control Panel",
            "panel_type": "main",
            "max_devices": 250,
            "properties": {
                "power_supply": "120VAC",
                "battery_capacity": "100AH",
                "communication_protocols": ["SLC", "NAC"],
            },
        },
    ]

    panel_added_count = 0
    for panel in new_panels:
        # Check if panel already exists
        cursor.execute(
            """
            SELECT COUNT(*) FROM panels
            WHERE model = ? AND manufacturer_id = ?
        """,
            (panel["model"], manufacturers.get(panel["manufacturer"], 1)),
        )

        if cursor.fetchone()[0] == 0:
            cursor.execute(
                """
                INSERT INTO panels (manufacturer_id, model, name, panel_type, max_devices, properties_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    manufacturers.get(panel["manufacturer"], 1),
                    panel["model"],
                    panel["name"],
                    panel["panel_type"],
                    panel["max_devices"],
                    json.dumps(panel["properties"]),
                ),
            )
            panel_added_count += 1

    conn.commit()
    conn.close()

    print("Device catalog populated successfully!")
    print(f"Added {added_count} new devices")
    print(f"Added {panel_added_count} new panels")
    print(f"Total manufacturers: {len(manufacturers)}")
    print(f"Total device types: {len(device_types)}")


if __name__ == "__main__":
    populate_devices()
