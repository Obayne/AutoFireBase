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
        """
    )
    coverage_tables.create_tables(con)
    con.commit()


def _id_for(cur, table, key, value):
    cur.execute(f"SELECT id FROM {table} WHERE {key}=?", (value,))
    row = cur.fetchone()
    if row:
        return row["id"]
    cur.execute(f"INSERT INTO {table}({key}) VALUES(?)", (value,))
    return cur.lastrowid


def seed_demo(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM devices")
    if cur.fetchone()["c"] > 0:
        return
    types = {
        "Detector": "Smokes/Heat",
        "Notification": "Strobes/HornStrobes/Speakers",
        "Initiating": "Pulls/Manual",
    }
    for code, desc in types.items():
        _id_for(cur, "device_types", "code", code)
    mfr_id = _id_for(cur, "manufacturers", "name", "(Any)")

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

    # Seed wire types
    wire_types = {
        "NAC": "Notification Appliance Circuit",
        "SLC": "Signaling Line Circuit",
        "Power": "Power Limited Circuit",
    }
    for code, desc in wire_types.items():
        _id_for(cur, "wire_types", "code", code)

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

    coverage_tables.populate_tables(con)
    con.commit()


def fetch_devices(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.name, d.symbol, dt.code AS type, m.name AS manufacturer, d.model AS part_number
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
