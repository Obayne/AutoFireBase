import json
import os
import sqlite3
from pathlib import Path

from db import coverage_tables

# This loader contains long SQL schema strings and seed data; allow E501 here.
# ruff: noqa: E501
# noqa: E501

DB_DEFAULT = os.path.join(os.path.expanduser("~"), "AutoFire", "catalog.db")


def connect(db_path: str | None = None):
    path = db_path or DB_DEFAULT
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def ensure_schema(con: sqlite3.Connection):
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS manufacturers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS device_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS devices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER,
            type_id INTEGER,
            model TEXT,
            name TEXT,
            symbol TEXT,
            properties_json TEXT,
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id),
            FOREIGN KEY(type_id) REFERENCES device_types(id)
        );
        CREATE TABLE IF NOT EXISTS device_specs(
            device_id INTEGER PRIMARY KEY,
            strobe_candela REAL,
            speaker_db_at10ft REAL,
            smoke_spacing_ft REAL,
            current_a REAL,
            voltage_v REAL,
            notes TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(id)
        );
        CREATE TABLE IF NOT EXISTS wire_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT
        );
        CREATE TABLE IF NOT EXISTS wires(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER,
            type_id INTEGER,
            gauge INTEGER,
            color TEXT,
            insulation TEXT,
            ohms_per_1000ft REAL,
            max_current_a REAL,
            model TEXT,
            name TEXT,
            properties_json TEXT,
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id),
            FOREIGN KEY(type_id) REFERENCES wire_types(id)
        );
        CREATE TABLE IF NOT EXISTS panels(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER,
            model TEXT NOT NULL,
            name TEXT,
            panel_type TEXT,  -- 'main', 'annunciator', 'power_supply', etc.
            max_devices INTEGER,
            properties_json TEXT,  -- Circuit configs, power specs, etc.
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id)
        );
        CREATE TABLE IF NOT EXISTS panel_circuits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER,
            circuit_type TEXT,  -- 'NAC', 'IDC', 'SLC', '485', etc.
            circuit_number INTEGER,
            max_devices INTEGER,
            max_current_a REAL,
            voltage_v REAL,
            properties_json TEXT,
            FOREIGN KEY(panel_id) REFERENCES panels(id)
        );
        CREATE TABLE IF NOT EXISTS panel_compatibility(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER,
            device_type_id INTEGER,
            compatible BOOLEAN DEFAULT 1,
            notes TEXT,
            FOREIGN KEY(panel_id) REFERENCES panels(id),
            FOREIGN KEY(device_type_id) REFERENCES device_types(id)
        );
        """
    )
    coverage_tables.create_tables(con)
    con.commit()


def _id_for(cur, table, key, value):
    # Handle different column naming conventions
    if table == "Manufacturers":
        id_col = "id"
        name_col = "name"
    elif table == "device_types":
        id_col = "id"
        name_col = "code"
    elif table == "wire_types":
        id_col = "id"
        name_col = "code"
    else:
        id_col = "id"
        name_col = "name"

    if key == "name":
        key = name_col

    cur.execute(f"SELECT {id_col} FROM {table} WHERE {key}=?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]  # Use index since row_factory might not be set
    cur.execute(f"INSERT INTO {table}({name_col}) VALUES(?)", (value,))
    return cur.lastrowid


def seed_demo(con: sqlite3.Connection):
    cur = con.cursor()

    # Always ensure panels exist, even if devices already exist
    # Check if panels exist (table might not exist yet)
    panel_count = 0
    try:
        cur.execute("SELECT COUNT(*) AS c FROM panels")
        panel_count = cur.fetchone()[0]
    except sqlite3.OperationalError:
        # Panels table doesn't exist yet
        pass

    # Only seed devices if they don't exist
    cur.execute("SELECT COUNT(*) AS c FROM devices")
    device_count = cur.fetchone()[0]

    if device_count == 0:
        # Seed devices and types
        types = {
            "Detector": "Smokes/Heat",
            "Notification": "Strobes/HornStrobes/Speakers",
            "Initiating": "Pulls/Manual",
        }
        for code, desc in types.items():
            _id_for(cur, "device_types", "code", code)
        mfr_id = _id_for(cur, "Manufacturers", "name", "(Any)")

        def add(dev):
            t_id = _id_for(cur, "device_types", "code", dev["type"])
            cur.execute(
                "INSERT INTO devices(manufacturer_id,type_id,model,name,symbol,properties_json) VALUES(?,?,?,?,?,?)",
                (
                    mfr_id,
                    t_id,
                    dev.get("part_number", ""),
                    dev["name"],
                    dev["symbol"],
                    json.dumps(dev.get("props", {})),
                ),
            )

        demo = [
            {"name": "Smoke Detector", "symbol": "SD", "type": "Detector", "part_number": "GEN-SD"},
            {"name": "Heat Detector", "symbol": "HD", "type": "Detector", "part_number": "GEN-HD"},
            {
                "name": "Strobe",
                "symbol": "S",
                "type": "Notification",
                "part_number": "GEN-S",
                "props": {"candelas": [15, 30, 75, 95, 110, 135, 185]},
            },
            {
                "name": "Horn Strobe",
                "symbol": "HS",
                "type": "Notification",
                "part_number": "GEN-HS",
                "props": {"candelas": [15, 30, 75, 95, 110, 135, 185]},
            },
            {"name": "Speaker", "symbol": "SPK", "type": "Notification", "part_number": "GEN-SPK"},
            {"name": "Pull Station", "symbol": "PS", "type": "Initiating", "part_number": "GEN-PS"},
        ]
        for d in demo:
            add(d)

    # Always seed panels if they don't exist
    if panel_count == 0:
        print("Seeding panels...")
        # Seed wire types first (needed for wires)
        wire_types = {
            "NAC": "Notification Appliance Circuit",
            "SLC": "Signaling Line Circuit",
            "Power": "Power Limited Circuit",
        }
        for code, desc in wire_types.items():
            _id_for(cur, "wire_types", "code", code)

        # Seed wires
        mfr_id = _id_for(cur, "Manufacturers", "name", "(Any)")

        def add_wire(wire):
            t_id = _id_for(cur, "wire_types", "code", wire["type"])
            cur.execute(
                "INSERT INTO wires(manufacturer_id,type_id,gauge,color,insulation,ohms_per_1000ft,max_current_a,model,name,properties_json) VALUES(?,?,?,?,?,?,?,?,?,?)",
                (
                    mfr_id,
                    t_id,
                    wire["gauge"],
                    wire["color"],
                    wire.get("insulation", "THHN"),
                    wire["ohms_per_1000ft"],
                    wire["max_current_a"],
                    wire.get("part_number", ""),
                    wire["name"],
                    json.dumps(wire.get("props", {})),
                ),
            )

        wire_demo = [
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
        for w in wire_demo:
            add_wire(w)

        # Seed panels
        # Use existing manufacturer or create new one
        cur.execute("SELECT id FROM manufacturers WHERE name=?", ("Honeywell Firelite",))
        row = cur.fetchone()
        if row:
            firelite_id = row[0]
        else:
            cur.execute("INSERT INTO manufacturers(name) VALUES(?)", ("Honeywell Firelite",))
            firelite_id = cur.lastrowid

        def add_panel(panel):
            print(f"Adding panel: {panel['model']}")
            cur.execute(
                "INSERT INTO panels(manufacturer_id,model,name,panel_type,max_devices,properties_json) VALUES(?,?,?,?,?,?)",
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
            print(f"Panel added with id: {panel_id}")

            # Add circuits
            for circuit in panel.get("circuits", []):
                cur.execute(
                    "INSERT INTO panel_circuits(panel_id,circuit_type,circuit_number,max_devices,max_current_a,voltage_v,properties_json) VALUES(?,?,?,?,?,?,?)",
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
            for compat in panel.get("compatibility", []):
                type_id = _id_for(cur, "device_types", "code", compat["device_type"])
                cur.execute(
                    "INSERT INTO panel_compatibility(panel_id,device_type_id,compatible,notes) VALUES(?,?,?,?)",
                    (panel_id, type_id, compat.get("compatible", True), compat.get("notes", "")),
                )

        panel_demo = [
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
                "compatibility": [
                    {"device_type": "Detector", "compatible": True},
                    {"device_type": "Notification", "compatible": True},
                    {"device_type": "Initiating", "compatible": True},
                ],
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
        for p in panel_demo:
            add_panel(p)

    coverage_tables.populate_tables(con)
    con.commit()


def fetch_devices(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.name as name, d.symbol as symbol, dt.code AS type, m.name AS manufacturer, d.model AS part_number
        FROM devices d
        LEFT JOIN manufacturers m ON m.id=d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id=d.type_id
        ORDER BY d.name
        """
    )
    return [dict(row) for row in cur.fetchall()]


def fetch_wires(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
        SELECT w.name, w.gauge, w.color, wt.code AS type, m.name AS manufacturer,
               w.ohms_per_1000ft, w.max_current_a, w.model AS part_number
        FROM wires w
        LEFT JOIN manufacturers m ON m.id=w.manufacturer_id
        LEFT JOIN wire_types wt ON wt.id=w.type_id
        ORDER BY w.gauge, w.name
        """
    )
    return [dict(row) for row in cur.fetchall()]


def fetch_layers(con: sqlite3.Connection):
    # Layers are UI organization constructs, not stored in database
    # Return default layer structure
    return [{"id": 1, "name": "Default", "visible": True}]


def strobe_radius_for_candela(con: sqlite3.Connection, cand: int) -> float | None:
    cur = con.cursor()
    cur.execute("SELECT radius_ft FROM strobe_candela WHERE candela=?", (int(cand),))
    r = cur.fetchone()
    return float(r["radius_ft"]) if r else None


def list_manufacturers(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT name FROM manufacturers ORDER BY name")
    return ["(Any)"] + [r["name"] for r in cur.fetchall()]


def list_types(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT code FROM device_types ORDER BY code")
    return ["(Any)"] + [r["code"] for r in cur.fetchall()]


def get_wall_strobe_candela(con: sqlite3.Connection, room_size: int) -> int | None:
    cur = con.cursor()
    cur.execute(
        f"SELECT candela FROM {coverage_tables.WALL_STROBE_TABLE_NAME} WHERE room_size >= ? ORDER BY room_size ASC LIMIT 1",
        (room_size,),
    )
    r = cur.fetchone()
    return int(r["candela"]) if r else None


def get_ceiling_strobe_candela(
    con: sqlite3.Connection, ceiling_height: int, room_size: int
) -> int | None:
    cur = con.cursor()
    cur.execute(
        f"SELECT candela FROM {coverage_tables.CEILING_STROBE_TABLE_NAME} WHERE ceiling_height >= ? AND room_size >= ? ORDER BY ceiling_height ASC, room_size ASC LIMIT 1",
        (
            ceiling_height,
            room_size,
        ),
    )
    r = cur.fetchone()
    return int(r["candela"]) if r else None


def fetch_panels(con: sqlite3.Connection):
    """Fetch all panels with their circuits and compatibility info."""
    cur = con.cursor()
    cur.execute(
        "SELECT p.id, p.manufacturer_id, p.model, p.name, p.panel_type, p.max_devices, p.properties_json, manufacturers.name as manufacturer_name FROM panels p LEFT JOIN manufacturers ON manufacturers.id = p.manufacturer_id ORDER BY manufacturers.name, p.model"
    )
    print("DEBUG: Query executed successfully")
    panels = []
    for row in cur.fetchall():
        # Convert row to dict manually
        panel = {
            "id": row[0],
            "manufacturer_id": row[1],
            "model": row[2],
            "name": row[3],
            "panel_type": row[4],
            "max_devices": row[5],
            "properties_json": row[6],
            "manufacturer_name": row[7],
        }
        panel_id = panel["id"]

        # Fetch circuits
        cur.execute(
            "SELECT * FROM panel_circuits WHERE panel_id = ? ORDER BY circuit_type, circuit_number",
            (panel_id,),
        )
        panel["circuits"] = []
        for r in cur.fetchall():
            circuit = {}
            for i, key in enumerate(r.keys()):
                circuit[key] = r[i]
            panel["circuits"].append(circuit)

        # Fetch compatibility
        cur.execute(
            """
            SELECT pc.*, dt.code as device_type
            FROM panel_compatibility pc
            LEFT JOIN device_types dt ON dt.id = pc.device_type_id
            WHERE pc.panel_id = ?
            """,
            (panel_id,),
        )
        panel["compatibility"] = []
        for r in cur.fetchall():
            compat = {}
            for i, key in enumerate(r.keys()):
                compat[key] = r[i]
            panel["compatibility"].append(compat)

        panels.append(panel)

    return panels


def fetch_compatible_devices(con: sqlite3.Connection, panel_id: int):
    """Fetch devices compatible with a specific panel."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.*, m.name as manufacturer_name, dt.code as type_name
        FROM devices d
        LEFT JOIN manufacturers m ON m.id = d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id = d.type_id
        WHERE d.type_id IN (
            SELECT device_type_id FROM panel_compatibility
            WHERE panel_id = ? AND compatible = 1
        )
        ORDER BY dt.code, d.name
        """,
        (panel_id,),
    )
    return [dict(row) for row in cur.fetchall()]


def list_panel_manufacturers(con: sqlite3.Connection):
    """List manufacturers that make panels."""
    cur = con.cursor()
    cur.execute(
        "SELECT DISTINCT m.name FROM manufacturers m JOIN panels p ON p.manufacturer_id = m.id ORDER BY m.name"
    )
    return [r["name"] for r in cur.fetchall()]
