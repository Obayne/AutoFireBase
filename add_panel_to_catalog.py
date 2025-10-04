"""
Add Fire Alarm Control Panel to the catalog database
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from db.loader import connect, ensure_schema


def add_panel_to_catalog():
    """Add fire alarm panel to the catalog database."""

    print("Adding Fire Alarm Control Panel to catalog...")

    # Connect to the default catalog database
    con = connect()
    ensure_schema(con)
    cursor = con.cursor()

    try:
        # Add Panel device type if it doesn't exist
        cursor.execute("SELECT id FROM device_types WHERE code = ?", ("Panel",))
        panel_type = cursor.fetchone()
        if not panel_type:
            cursor.execute(
                "INSERT INTO device_types (code, description) VALUES (?, ?)",
                ("Panel", "Fire Alarm Control Panel"),
            )
            panel_type_id = cursor.lastrowid
            print(f"✅ Added Panel device type (ID: {panel_type_id})")
        else:
            panel_type_id = panel_type["id"]
            print(f"✅ Panel device type already exists (ID: {panel_type_id})")

        # Ensure we have a manufacturer
        cursor.execute("SELECT id FROM manufacturers WHERE name = ?", ("Notifier",))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            cursor.execute("INSERT INTO manufacturers (name) VALUES (?)", ("Notifier",))
            manufacturer_id = cursor.lastrowid
            print(f"✅ Added Notifier manufacturer (ID: {manufacturer_id})")
        else:
            manufacturer_id = manufacturer["id"]
            print(f"✅ Notifier manufacturer exists (ID: {manufacturer_id})")

        # Add fire alarm panel device if it doesn't exist
        cursor.execute("SELECT id FROM devices WHERE name = ?", ("Fire Alarm Control Panel",))
        panel_device = cursor.fetchone()
        if not panel_device:
            cursor.execute(
                """INSERT INTO devices
                            (manufacturer_id, type_id, model, name, symbol, properties_json)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    manufacturer_id,
                    panel_type_id,
                    "NFS2-3030",
                    "Fire Alarm Control Panel",
                    "■",
                    "{}",
                ),
            )
            print("✅ Added Fire Alarm Control Panel to catalog")
        else:
            print("✅ Fire Alarm Control Panel already exists in catalog")

        con.commit()

        # Verify by fetching all devices
        from db.loader import fetch_devices

        devices = fetch_devices(con)
        print(f"\nCatalog now contains {len(devices)} devices:")
        for device in devices:
            name = device.get("name", "Unknown")
            device_type = device.get("type", "Unknown")
            symbol = device.get("symbol", "?")
            print(f"  - {name}: {device_type} ({symbol})")

        con.close()
        return True

    except Exception as e:
        print(f"❌ Error adding panel to catalog: {e}")
        con.rollback()
        con.close()
        return False


if __name__ == "__main__":
    success = add_panel_to_catalog()
    if success:
        print("\n🎉 Fire Alarm Control Panel successfully added to catalog!")
        print("You can now place it in the AutoFire application.")
    else:
        sys.exit(1)
