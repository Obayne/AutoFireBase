#!/usr/bin/env python3
"""
Rebuild database from XLS export and add panel functionality.
"""

import json
import os
import sqlite3
from pathlib import Path

import pandas as pd

# Database path
DB_PATH = os.path.join(os.path.expanduser("~"), "AutoFire", "catalog.db")


def rebuild_database():
    """Rebuild the database from XLS export."""

    print("Rebuilding database from XLS export...")

    # Remove existing database
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing database: {DB_PATH}")

    # Ensure directory exists
    Path(os.path.dirname(DB_PATH)).mkdir(parents=True, exist_ok=True)

    # Create new database
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Create tables based on XLS structure
    create_tables(cur)

    # Import XLS data
    import_xls_data(cur)

    # Add panel schema
    add_panel_schema(cur)

    # Seed panels
    seed_panels(cur)

    con.commit()
    con.close()

    print("Database rebuild complete!")


def create_tables(cur):
    """Create database tables based on XLS structure."""
    print("Creating database tables...")

    # Manufacturers table
    cur.execute(
        """
        CREATE TABLE Manufacturers(
            ManufacturerId TEXT PRIMARY KEY,
            Name TEXT UNIQUE NOT NULL,
            Website TEXT
        );
    """
    )

    # Devices table (based on XLS columns)
    cur.execute(
        """
        CREATE TABLE Devices(
            DeviceId TEXT PRIMARY KEY,
            DefaultBlockName TEXT,
            RiserBlockName TEXT,
            PTPBlockName TEXT,
            BlockOrientation TEXT,
            ManufacturerId TEXT,
            ProductLine TEXT,
            Category TEXT,
            SubCategory1 TEXT,
            SubCategory2 TEXT,
            SubCategory3 TEXT,
            PartType TEXT,
            IsPassThrough INTEGER,
            PartNo TEXT,
            Model TEXT,
            Description TEXT,
            AddressQuantity REAL,
            ReqdStandbyCurrent REAL,
            ReqdAlarmCurrent REAL,
            AddlCurrent REAL,
            AddlWatts REAL,
            NominalVoltage REAL,
            MinVoltage REAL,
            AddCardCurrentToBatteryCalc INTEGER,
            IsCeilingMount INTEGER,
            Mounting TEXT,
            Box TEXT,
            Size TEXT,
            Trim TEXT,
            DefaultColor TEXT,
            DefaultLayer TEXT,
            DefaultScale REAL,
            ExcludeFromReport INTEGER,
            ExcludeFromRiser INTEGER,
            ExcludeFromLegend INTEGER,
            ReportSequence INTEGER,
            Approvals TEXT,
            Chicago TEXT,
            CSFM TEXT,
            FM TEXT,
            UL TEXT,
            ULC TEXT,
            NYCBSA TEXT,
            NYCMEA TEXT,
            CardBatteryChargingCapacities TEXT,
            CardBatteryQuantity INTEGER,
            AssemblyBatterySizeList TEXT,
            AssemblyTotalAvailableCurrent REAL,
            AssemblyTotalAvailableWatts REAL,
            GenerateBatteryCalculation INTEGER,
            HoleQty INTEGER,
            ListPrice REAL,
            CustomProperties TEXT,
            PDFFilePath TEXT,
            DetailDrawingPath TEXT,
            CreatedByUser TEXT,
            CreatedDateTime TEXT,
            EditiedByUser TEXT,
            LastEditDateTime TEXT,
            Notes TEXT,
            DeviceTypeTemplates TEXT,
            CircuitTemplates TEXT,
            FOREIGN KEY(ManufacturerId) REFERENCES Manufacturers(ManufacturerId)
        );
    """
    )

    # Device types table
    cur.execute(
        """
        CREATE TABLE device_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT
        );
    """
    )

    # Device specs table
    cur.execute(
        """
        CREATE TABLE device_specs(
            device_id TEXT PRIMARY KEY,
            strobe_candela REAL,
            speaker_db_at10ft REAL,
            current_a REAL,
            voltage_v REAL,
            notes TEXT,
            FOREIGN KEY(device_id) REFERENCES Devices(DeviceId)
        );
    """
    )


def import_xls_data(cur):
    """Import data from XLS file."""
    print("Importing XLS data...")

    # Read XLS file
    df = pd.read_excel("Device import.xlsx")

    # Import manufacturers
    manufacturers = df["Manufacturer"].dropna().unique()
    for manufacturer in manufacturers:
        manufacturer_id = str(hash(manufacturer))  # Simple ID generation
        cur.execute(
            "INSERT OR IGNORE INTO Manufacturers(ManufacturerId, Name) VALUES(?, ?)",
            (manufacturer_id, manufacturer),
        )

    # Import devices
    for _, row in df.iterrows():
        manufacturer_id = str(hash(row["Manufacturer"])) if pd.notna(row["Manufacturer"]) else None

        # Convert boolean columns
        bool_cols = [
            "IsPassThrough",
            "AddCardCurrentToBatteryCalc",
            "IsCeilingMount",
            "ExcludeFromReport",
            "ExcludeFromRiser",
            "ExcludeFromLegend",
            "GenerateBatteryCalculation",
        ]
        for col in bool_cols:
            if col in row and pd.notna(row[col]):
                row[col] = 1 if str(row[col]).lower() in ("true", "1", "yes") else 0

        cur.execute(
            """
            INSERT INTO Devices(
                DeviceId, DefaultBlockName, RiserBlockName, PTPBlockName, BlockOrientation,
                ManufacturerId, ProductLine, Category, SubCategory1, SubCategory2, SubCategory3,
                PartType, IsPassThrough, PartNo, Model, Description, AddressQuantity,
                ReqdStandbyCurrent, ReqdAlarmCurrent, AddlCurrent, AddlWatts, NominalVoltage,
                MinVoltage, AddCardCurrentToBatteryCalc, IsCeilingMount, Mounting, Box, Size, Trim,
                DefaultColor, DefaultLayer, DefaultScale, ExcludeFromReport, ExcludeFromRiser,
                ExcludeFromLegend, ReportSequence, Approvals, Chicago, CSFM, FM, UL, ULC,
                NYCBSA, NYCMEA, CardBatteryChargingCapacities, CardBatteryQuantity,
                AssemblyBatterySizeList, AssemblyTotalAvailableCurrent, AssemblyTotalAvailableWatts,
                GenerateBatteryCalculation, HoleQty, ListPrice, CustomProperties, PDFFilePath,
                DetailDrawingPath, CreatedByUser, CreatedDateTime, EditiedByUser, LastEditDateTime,
                Notes, DeviceTypeTemplates, CircuitTemplates
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            tuple(row),
        )

    print(f"Imported {len(df)} devices")


def add_panel_schema(cur):
    """Add panel-related tables."""
    print("Adding panel schema...")

    cur.execute(
        """
        CREATE TABLE panels(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id TEXT,
            model TEXT NOT NULL,
            name TEXT,
            panel_type TEXT,
            max_devices INTEGER,
            properties_json TEXT,
            FOREIGN KEY(manufacturer_id) REFERENCES Manufacturers(ManufacturerId)
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE panel_circuits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER,
            circuit_type TEXT,
            circuit_number INTEGER,
            max_devices INTEGER,
            max_current_a REAL,
            voltage_v REAL,
            properties_json TEXT,
            FOREIGN KEY(panel_id) REFERENCES panels(id)
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE panel_compatibility(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER,
            device_type_id INTEGER,
            compatible INTEGER DEFAULT 1,
            notes TEXT,
            FOREIGN KEY(panel_id) REFERENCES panels(id),
            FOREIGN KEY(device_type_id) REFERENCES device_types(id)
        );
    """
    )

    # Wire-related tables
    cur.execute(
        """
        CREATE TABLE wire_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT
        );
    """
    )

    cur.execute(
        """
        CREATE TABLE wires(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id TEXT,
            type_id INTEGER,
            gauge INTEGER,
            color TEXT,
            insulation TEXT,
            ohms_per_1000ft REAL,
            max_current_a REAL,
            model TEXT,
            name TEXT,
            properties_json TEXT,
            FOREIGN KEY(manufacturer_id) REFERENCES Manufacturers(ManufacturerId),
            FOREIGN KEY(type_id) REFERENCES wire_types(id)
        );
    """
    )


def seed_panels(cur):
    """Seed panel data."""
    print("Seeding panels...")

    # Seed device types
    device_types = {
        "Detector": "Smoke/Heat Detectors",
        "Notification": "Strobes/HornStrobes/Speakers",
        "Initiating": "Pull Stations/Manual Devices",
    }
    for code, desc in device_types.items():
        cur.execute("INSERT INTO device_types(code, description) VALUES(?, ?)", (code, desc))

    # Seed wire types
    wire_types = {
        "NAC": "Notification Appliance Circuit",
        "SLC": "Signaling Line Circuit",
        "Power": "Power Limited Circuit",
    }
    for code, desc in wire_types.items():
        cur.execute("INSERT INTO wire_types(code, description) VALUES(?, ?)", (code, desc))

    # Seed wires
    wires = [
        {
            "name": "14 AWG Red THHN",
            "gauge": 14,
            "color": "Red",
            "type": "NAC",
            "ohms_per_1000ft": 2.525,
            "max_current_a": 15,
            "part_number": "14THHN-RED",
        },
        {
            "name": "14 AWG Black THHN",
            "gauge": 14,
            "color": "Black",
            "type": "NAC",
            "ohms_per_1000ft": 2.525,
            "max_current_a": 15,
            "part_number": "14THHN-BLK",
        },
        {
            "name": "16 AWG Red THHN",
            "gauge": 16,
            "color": "Red",
            "type": "SLC",
            "ohms_per_1000ft": 4.016,
            "max_current_a": 10,
            "part_number": "16THHN-RED",
        },
        {
            "name": "16 AWG Yellow THHN",
            "gauge": 16,
            "color": "Yellow",
            "type": "SLC",
            "ohms_per_1000ft": 4.016,
            "max_current_a": 10,
            "part_number": "16THHN-YEL",
        },
        {
            "name": "18 AWG Red THHN",
            "gauge": 18,
            "color": "Red",
            "type": "Power",
            "ohms_per_1000ft": 6.385,
            "max_current_a": 7,
            "part_number": "18THHN-RED",
        },
        {
            "name": "18 AWG Black THHN",
            "gauge": 18,
            "color": "Black",
            "type": "Power",
            "ohms_per_1000ft": 6.385,
            "max_current_a": 7,
            "part_number": "18THHN-BLK",
        },
    ]

    for wire in wires:
        type_id = cur.execute("SELECT id FROM wire_types WHERE code=?", (wire["type"],)).fetchone()[
            0
        ]
        manufacturer_id = str(hash("(Any)"))  # Use same ID as devices
        cur.execute(
            """
            INSERT INTO wires(manufacturer_id, type_id, gauge, color, insulation, ohms_per_1000ft, max_current_a, model, name)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                manufacturer_id,
                type_id,
                wire["gauge"],
                wire["color"],
                "THHN",
                wire["ohms_per_1000ft"],
                wire["max_current_a"],
                wire.get("part_number"),
                wire["name"],
            ),
        )

    # Seed panels
    firelite_id = str(hash("Honeywell Firelite"))
    cur.execute(
        "INSERT INTO Manufacturers(ManufacturerId, Name) VALUES(?, ?) ON CONFLICT(ManufacturerId) DO NOTHING",
        (firelite_id, "Honeywell Firelite"),
    )

    panels = [
        {
            "model": "MS-9050UD",
            "name": "MS-9050UD Fire Alarm Control Panel",
            "panel_type": "main",
            "max_devices": 1000,
            "props": {
                "power_supply": "120VAC",
                "battery_capacity": "55AH",
                "communication_protocols": ["SLC", "NAC", "485"],
            },
            "circuits": [
                {
                    "type": "SLC",
                    "number": 1,
                    "max_devices": 159,
                    "props": {"loop_type": "Class A/B"},
                },
                {
                    "type": "NAC",
                    "number": 1,
                    "max_current_a": 3.0,
                    "voltage_v": 24,
                    "max_devices": 100,
                },
                {
                    "type": "NAC",
                    "number": 2,
                    "max_current_a": 3.0,
                    "voltage_v": 24,
                    "max_devices": 100,
                },
                {"type": "IDC", "number": 1, "max_devices": 10, "props": {"supervised": True}},
                {"type": "485", "number": 1, "props": {"protocol": "Modbus"}},
            ],
            "compatibility": ["Detector", "Notification", "Initiating"],
        },
        {
            "model": "ANN-80",
            "name": "ANN-80 Remote Annunciator",
            "panel_type": "annunciator",
            "max_devices": 0,
            "props": {
                "display_type": "LCD",
                "zones": 80,
            },
            "circuits": [
                {"type": "485", "number": 1, "props": {"protocol": "Panel Link"}},
            ],
            "compatibility": [],  # Annunciators don't directly connect devices
        },
    ]

    for panel in panels:
        cur.execute(
            """
            INSERT INTO panels(manufacturer_id, model, name, panel_type, max_devices, properties_json)
            VALUES(?, ?, ?, ?, ?, ?)
        """,
            (
                firelite_id,
                panel["model"],
                panel["name"],
                panel["panel_type"],
                panel["max_devices"],
                json.dumps(panel.get("props", {})),
            ),
        )
        panel_id = cur.lastrowid

        # Add circuits
        for circuit in panel.get("circuits", []):
            cur.execute(
                """
                INSERT INTO panel_circuits(panel_id, circuit_type, circuit_number, max_devices, max_current_a, voltage_v, properties_json)
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    panel_id,
                    circuit["type"],
                    circuit["number"],
                    circuit.get("max_devices", 0),
                    circuit.get("max_current_a", 0),
                    circuit.get("voltage_v", 0),
                    json.dumps(circuit.get("props", {})),
                ),
            )

        # Add device compatibility
        for device_type in panel.get("compatibility", []):
            type_id = cur.execute(
                "SELECT id FROM device_types WHERE code=?", (device_type,)
            ).fetchone()[0]
            cur.execute(
                """
                INSERT INTO panel_compatibility(panel_id, device_type_id, compatible)
                VALUES(?, ?, 1)
            """,
                (panel_id, type_id),
            )

    print("Panel seeding complete!")


if __name__ == "__main__":
    rebuild_database()
