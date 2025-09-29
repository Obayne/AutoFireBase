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
    # Allow override via env var for flexibility in CI/dev
    env_path = os.environ.get("AUTOFIRE_DB_PATH")
    path = db_path or env_path or DB_DEFAULT
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
        """
    )
    coverage_tables.create_tables(con)
    con.commit()


def _id_for(cur, table, key, value):
    cur.execute(f"SELECT id FROM {table} WHERE {key}=?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table}({key}) VALUES(?)", (value,))
    return cur.lastrowid


def seed_demo(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM devices")
    result = cur.fetchone()
    if result and result[0] > 0:
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
        # NFPA 170 Fire Safety Symbols
        {"name": "Exit Sign", "symbol": "EXIT", "type": "NFPA 170", "part_number": "NFPA-EXIT"},
        {
            "name": "Directional Arrow Right",
            "symbol": "\u2192",
            "type": "NFPA 170",
            "part_number": "NFPA-ARROW-R",
        },
        {
            "name": "Directional Arrow Left",
            "symbol": "\u2190",
            "type": "NFPA 170",
            "part_number": "NFPA-ARROW-L",
        },
        {
            "name": "Directional Arrow Up",
            "symbol": "\u2191",
            "type": "NFPA 170",
            "part_number": "NFPA-ARROW-U",
        },
        {
            "name": "Directional Arrow Down",
            "symbol": "\u2193",
            "type": "NFPA 170",
            "part_number": "NFPA-ARROW-D",
        },
        {
            "name": "Fire Extinguisher",
            "symbol": "EXT",
            "type": "NFPA 170",
            "part_number": "NFPA-EXT",
        },
        {"name": "Fire Hose", "symbol": "HOSE", "type": "NFPA 170", "part_number": "NFPA-HOSE"},
        {"name": "Fire Alarm", "symbol": "ALARM", "type": "NFPA 170", "part_number": "NFPA-ALARM"},
    ]
    for d in demo:
        add(d)
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


def fetch_layers(con: sqlite3.Connection):
    # Layers are UI organization constructs, not stored in database
    # Return default layer structure
    return [{"id": 1, "name": "Default", "visible": True}]


def strobe_radius_for_candela(con: sqlite3.Connection, cand: int) -> float | None:
    cur = con.cursor()
    cur.execute("SELECT radius_ft FROM strobe_candela WHERE candela=?", (int(cand),))
    r = cur.fetchone()
    return float(r[0]) if r else None


def list_manufacturers(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT name FROM manufacturers ORDER BY name")
    return ["(Any)"] + [r[0] for r in cur.fetchall()]


def list_types(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT code FROM device_types ORDER BY code")
    return ["(Any)"] + [r[0] for r in cur.fetchall()]


def get_device_types(con: sqlite3.Connection):
    """Get all available device types."""
    cur = con.cursor()
    cur.execute("SELECT DISTINCT code FROM device_types ORDER BY code")
    return [r["code"] for r in cur.fetchall()]


def get_devices_by_type(con: sqlite3.Connection, device_type: str):
    """Get devices of a specific type."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.name, d.symbol, dt.code AS type, m.name AS manufacturer, d.model AS part_number
        FROM devices d
        LEFT JOIN manufacturers m ON m.id=d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id=d.type_id
        WHERE dt.code = ?
        ORDER BY d.name
        """,
        (device_type,),
    )
    return [dict(row) for row in cur.fetchall()]


def get_wall_strobe_candela(con: sqlite3.Connection, room_size: int) -> int | None:
    cur = con.cursor()
    cur.execute(
        f"SELECT candela FROM {coverage_tables.WALL_STROBE_TABLE_NAME} WHERE room_size >= ? ORDER BY room_size ASC LIMIT 1",
        (room_size,),
    )
    r = cur.fetchone()
    return int(r[0]) if r else None


def search_devices(
    con: sqlite3.Connection, search_text: str = "", device_type: str = "", manufacturer: str = ""
):
    """Search devices by name, manufacturer, model, and optionally filter by type and manufacturer."""
    cur = con.cursor()

    query = """
        SELECT d.id, d.name, d.symbol, dt.code AS type, m.name AS manufacturer, d.model
        FROM devices d
        LEFT JOIN manufacturers m ON m.id=d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id=d.type_id
        WHERE 1=1
    """
    params = []

    if search_text:
        query += " AND (d.name LIKE ? OR m.name LIKE ? OR d.model LIKE ?)"
        search_param = f"%{search_text}%"
        params.extend([search_param, search_param, search_param])

    if device_type:
        query += " AND dt.code = ?"
        params.append(device_type)

    if manufacturer:
        query += " AND m.name = ?"
        params.append(manufacturer)

    query += " ORDER BY dt.code, d.name"

    cur.execute(query, params)
    return [dict(row) for row in cur.fetchall()]
