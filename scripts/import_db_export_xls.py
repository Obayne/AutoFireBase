"""
Script to import and normalize panel/device data from 'Projects/DB Export new xls' Excel file.
- Extracts manufacturer, model, voltage, type, etc.
- Normalizes manufacturer names using alias map.
- Prepares data for DB integration.
"""

import os

import pandas as pd

# Path to the Excel file
XLS_PATH = os.path.join(os.path.dirname(__file__), "..", "Projects", "DB Export", "Device.xlsx")

# Manufacturer alias map (expand as needed)
MANUFACTURER_ALIASES = {
    "Honeywell>Firelite": "Fire-Lite Alarms",
    "Honeywell Firelite": "Fire-Lite Alarms",
    "FIRELITE": "Fire-Lite Alarms",
    "FIRE-LITE": "Fire-Lite Alarms",
    "Notifier": "NOTIFIER",
    "Honeywell>Notifier": "NOTIFIER",
    "Gamewell": "Gamewell-FCI",
    "Silent Knight": "Silent Knight",
    "System Sensor": "System Sensor",
    "VESDA": "Xtralis/VESDA",
    # Add more as needed
}


def normalize_manufacturer(name):
    if not isinstance(name, str):
        return name
    for alias, canonical in MANUFACTURER_ALIASES.items():
        if name.strip().lower().replace(" ", "").startswith(alias.lower().replace(" ", "")):
            return canonical
    return name.strip()


def main():
    # Read Excel file (auto-detect sheet)
    xls = pd.ExcelFile(XLS_PATH)
    sheet = xls.sheet_names[0]
    df = pd.read_excel(xls, sheet)
    # Show columns for reference
    print("Columns:", list(df.columns))
    # Normalize manufacturer
    df["manufacturer_normalized"] = df["Manufacturer"].apply(normalize_manufacturer)
    # Print sample rows
    print(
        df[
            [
                c
                for c in [
                    "Manufacturer",
                    "manufacturer_normalized",
                    "Model",
                    "PartType",
                    "NominalVoltage",
                ]
                if c in df.columns
            ]
        ].head(10)
    )
    # Save as CSV for reference
    out_path = os.path.join(
        os.path.dirname(__file__), "..", "artifacts", "db_export_normalized.csv"
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Normalized data saved to {out_path}")

    # --- Create SQLite database from DataFrame ---
    import sqlite3

    db_path = os.path.join(os.path.dirname(__file__), "..", "artifacts", "db_export_from_xls.db")
    print(f"Creating SQLite database at {db_path}")
    conn = sqlite3.connect(db_path)
    # Use a table name based on sheet or generic
    table_name = "imported_panels_devices"
    # Drop table if exists
    conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    # Infer schema from DataFrame
    df.to_sql(table_name, conn, index=False)
    print(f"Table {table_name} created with {len(df)} rows.")
    conn.close()
    print(f"SQLite database created at {db_path}")


if __name__ == "__main__":
    main()
