"""Add Fire Alarm Control Panel to the catalog database."""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


from db.loader import connect, ensure_schema


def add_panel_to_catalog() -> bool:
    """Add fire alarm panel to the catalog database.

    Returns True on success, False on failure.
    """
    # Configure logging (best-effort)
    try:
        from backend.logging_config import setup_logging

        setup_logging()
    except Exception:
        logging.basicConfig()
    logger = logging.getLogger(__name__)
    logger.info("Adding Fire Alarm Control Panel to catalog...")

    con = None
    try:
        # Connect to the default catalog database
        con = connect()
        ensure_schema(con)
        cursor = con.cursor()

        # Add Panel device type if it doesn't exist
        cursor.execute("SELECT id FROM device_types WHERE code = ?", ("Panel",))
        panel_type = cursor.fetchone()
        if not panel_type:
            cursor.execute(
                "INSERT INTO device_types (code, description) VALUES (?, ?)",
                ("Panel", "Fire Alarm Control Panel"),
            )
            panel_type_id = cursor.lastrowid
            logger.info("✅ Added Panel device type (ID: %s)", panel_type_id)
        else:
            # panel_type may be a mapping or tuple; try to get id
            try:
                panel_type_id = panel_type["id"]
            except Exception:
                panel_type_id = panel_type[0]
            logger.info("✅ Panel device type already exists (ID: %s)", panel_type_id)

        # Ensure we have a manufacturer
        cursor.execute("SELECT id FROM manufacturers WHERE name = ?", ("Notifier",))
        manufacturer = cursor.fetchone()
        if not manufacturer:
            cursor.execute("INSERT INTO manufacturers (name) VALUES (?)", ("Notifier",))
            manufacturer_id = cursor.lastrowid
            logger.info("✅ Added Notifier manufacturer (ID: %s)", manufacturer_id)
        else:
            try:
                manufacturer_id = manufacturer["id"]
            except Exception:
                manufacturer_id = manufacturer[0]
            logger.info("✅ Notifier manufacturer exists (ID: %s)", manufacturer_id)

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
            logger.info("✅ Added Fire Alarm Control Panel to catalog")
        else:
            logger.info("✅ Fire Alarm Control Panel already exists in catalog")

        con.commit()

        # Verify by fetching all devices
        from db.loader import fetch_devices

        devices = fetch_devices(con)
        logger.info("Catalog now contains %d devices", len(devices))
        for device in devices:
            name = device.get("name", "Unknown")
            device_type = device.get("type", "Unknown")
            symbol = device.get("symbol", "?")
            logger.debug(" - %s: %s (%s)", name, device_type, symbol)

        con.close()
        return True

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.exception("❌ Error adding panel to catalog: %s", e)
        try:
            if con is not None:
                con.rollback()
                con.close()
        except Exception:
            pass
        return False


if __name__ == "__main__":
    success = add_panel_to_catalog()
    logger = logging.getLogger(__name__)
    if success:
        logger.info("🎉 Fire Alarm Control Panel successfully added to catalog!")
        logger.info("You can now place it in the AutoFire application.")
    else:
        sys.exit(1)
