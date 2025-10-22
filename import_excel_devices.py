#!/usr/bin/env python3
"""
Import fire alarm devices from Excel file to AutoFire database.
This script processes the comprehensive device catalog and populates the database.
"""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd


def load_excel_data(file_path):
    """Load and return the Excel device data."""
    print(f"Loading Excel data from: {file_path}")
    df = pd.read_excel(file_path, sheet_name="Database Devices")
    print(f"Loaded {len(df):,} devices from Excel")
    return df


def get_manufacturer_mapping(cursor):
    """Get mapping of manufacturer name to ID."""
    cursor.execute("SELECT id, name FROM manufacturers;")
    return {name: mfg_id for mfg_id, name in cursor.fetchall()}


def get_device_type_mapping(cursor):
    """Get mapping of category description to device type ID."""
    cursor.execute("SELECT id, description FROM device_types;")
    return {desc: type_id for type_id, desc in cursor.fetchall()}


def create_properties_json(row):
    """Create properties JSON from Excel row data."""
    properties = {}

    # Technical specifications
    technical_fields = [
        "ReqdStandbyCurrent",
        "ReqdAlarmCurrent",
        "AddlCurrent",
        "AddlWatts",
        "NominalVoltage",
        "MinVoltage",
        "AddressQuantity",
        "IsCeilingMount",
        "Mounting",
        "Box",
        "Size",
        "Trim",
        "DefaultColor",
        "DefaultScale",
    ]

    for field in technical_fields:
        if pd.notna(row[field]):
            properties[field] = row[field]

    # Approval and certification info
    approval_fields = ["Approvals", "Chicago", "CSFM", "FM", "UL", "ULC", "NYCBSA", "NYCMEA"]
    approvals = {}
    for field in approval_fields:
        if pd.notna(row[field]):
            approvals[field] = row[field]
    if approvals:
        properties["Approvals"] = approvals

    # CAD and display properties
    cad_fields = [
        "DefaultBlockName",
        "RiserBlockName",
        "BlockOrientation",
        "DefaultLayer",
        "ExcludeFromReport",
        "ExcludeFromRiser",
        "ExcludeFromLegend",
    ]
    cad_props = {}
    for field in cad_fields:
        if pd.notna(row[field]):
            cad_props[field] = row[field]
    if cad_props:
        properties["CAD"] = cad_props

    # Additional metadata
    if pd.notna(row["ProductLine"]):
        properties["ProductLine"] = row["ProductLine"]
    if pd.notna(row["DeviceId"]):
        properties["OriginalDeviceId"] = row["DeviceId"]
    if pd.notna(row["Notes"]):
        properties["Notes"] = row["Notes"]

    return json.dumps(properties) if properties else None


def import_devices(df, cursor, mfg_mapping, type_mapping):
    """Import devices from DataFrame to database."""
    print("Starting device import...")

    imported_count = 0
    skipped_count = 0
    error_count = 0

    for index, row in df.iterrows():
        try:
            # Skip if missing essential data
            if pd.isna(row["PartNo"]) or not row["PartNo"].strip():
                skipped_count += 1
                continue

            # Get manufacturer ID
            manufacturer_id = None
            if pd.notna(row["Manufacturer"]):
                manufacturer_id = mfg_mapping.get(row["Manufacturer"])

            # Get device type ID
            type_id = None
            if pd.notna(row["Category"]):
                type_id = type_mapping.get(row["Category"])

            # Prepare device data
            model = str(row["PartNo"]).strip()
            name = str(row["Description"]).strip() if pd.notna(row["Description"]) else model
            symbol = None  # We'll need to map this later based on category
            properties_json = create_properties_json(row)

            # Insert device
            cursor.execute(
                """
                INSERT INTO devices (manufacturer_id, type_id, model, name, symbol, properties_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (manufacturer_id, type_id, model, name, symbol, properties_json),
            )

            imported_count += 1

            # Progress indicator
            if imported_count % 1000 == 0:
                print(f"  Imported {imported_count:,} devices...")

        except Exception as e:
            error_count += 1
            if error_count <= 10:  # Only show first 10 errors
                print(f"  Error importing device {row.get('PartNo', 'UNKNOWN')}: {e}")

    print(
        "Import complete: "
        + f"{imported_count:,} imported, "
        + f"{skipped_count:,} skipped, "
        + f"{error_count:,} errors"
    )
    return imported_count


def main():
    """Main import function."""
    # File paths
    excel_file = Path("c:/Dev/Autofire/Device import.xlsx")
    db_file = Path("c:/Dev/Autofire/autofire.db")

    if not excel_file.exists():
        print(f"Error: Excel file not found: {excel_file}")
        return 1

    if not db_file.exists():
        print(f"Error: Database file not found: {db_file}")
        return 1

    # Load Excel data
    df = load_excel_data(excel_file)

    # Connect to database
    print("Connecting to database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    try:
        # Get existing record count
        cursor.execute("SELECT COUNT(*) FROM devices;")
        initial_count = cursor.fetchone()[0]
        print(f"Database currently has {initial_count} devices")

        # Get mappings
        print("Loading manufacturer and device type mappings...")
        mfg_mapping = get_manufacturer_mapping(cursor)
        type_mapping = get_device_type_mapping(cursor)

        print(f"Found {len(mfg_mapping)} manufacturers and {len(type_mapping)} device types")

        # Import devices
        imported_count = import_devices(df, cursor, mfg_mapping, type_mapping)

        # Commit changes
        print("Committing changes to database...")
        conn.commit()

        # Verify final count
        cursor.execute("SELECT COUNT(*) FROM devices;")
        final_count = cursor.fetchone()[0]

        print("\nImport Summary:")
        print(f"  Initial device count: {initial_count:,}")
        print(f"  Devices imported: {imported_count:,}")
        print(f"  Final device count: {final_count:,}")
        print(f"  Net increase: {final_count - initial_count:,}")

    except Exception as e:
        print(f"Error during import: {e}")
        conn.rollback()
        return 1
    finally:
        conn.close()

    print("Import completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
