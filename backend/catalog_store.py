import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from db.schema import ensure_db


def get_catalog_path() -> str:
    home = Path(os.path.expanduser("~"))
    base = home / "AutoFire"
    base.mkdir(parents=True, exist_ok=True)
    return str(base / "catalog.db")

# SQL and long docstrings are intentional; allow E501 for this file.
# ruff: noqa: E501
# noqa: E501


def _connect() -> sqlite3.Connection:
    path = get_catalog_path()
    ensure_db(path)
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def seed_defaults() -> None:
    con = _connect(); cur = con.cursor()
    # Seed device types
    types = [
        ("strobe", "Strobe / Notification Appliance"),
        ("speaker", "Speaker / Audio Appliance"),
        ("smoke", "Smoke / Heat / Detector"),
        ("pull", "Pull Station"),
        ("panel", "Fire Alarm Panel"),
    ]
    for code, desc in types:
        cur.execute("INSERT OR IGNORE INTO device_types(code, description) VALUES(?,?)", (code, desc))
    # Seed a manufacturer
    cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES(?)", ("Generic",))
    con.commit(); con.close()


def add_device(manufacturer: str, type_code: str, model: str, name: str, symbol: str = "", specs: Optional[Dict[str, Any]] = None) -> int:
    con = _connect(); cur = con.cursor()
    # manufacturer id
    cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES(?)", (manufacturer,))
    cur.execute("SELECT id FROM manufacturers WHERE name=?", (manufacturer,))
    mid = cur.fetchone()[0]
    # type id
    cur.execute("SELECT id FROM device_types WHERE code=?", (type_code,))
    row = cur.fetchone()
    if not row:
        raise ValueError(f"Unknown device type code: {type_code}")
    tid = row[0]
    props = json.dumps({})
    cur.execute(
        "INSERT INTO devices(manufacturer_id,type_id,model,name,symbol,properties_json) VALUES(?,?,?,?,?,?)",
        (mid, tid, model, name, symbol, props),
    )
    did = cur.lastrowid
    if specs:
        cur.execute(
            "INSERT OR REPLACE INTO device_specs(device_id, strobe_candela, speaker_db_at10ft, smoke_spacing_ft, current_a, voltage_v, notes) VALUES(?,?,?,?,?,?,?)",
            (
                did,
                specs.get("strobe_candela"),
                specs.get("speaker_db_at10ft"),
                specs.get("smoke_spacing_ft"),
                specs.get("current_a"),
                specs.get("voltage_v"),
                specs.get("notes"),
            ),
        )
    con.commit(); con.close()
    return did


def list_devices(type_code: Optional[str] = None) -> List[Dict[str, Any]]:
    con = _connect(); cur = con.cursor()
    if type_code:
        cur.execute(
            """
            SELECT d.id, m.name AS manufacturer, dt.code AS type, d.model, d.name, d.symbol
            FROM devices d
            LEFT JOIN manufacturers m ON m.id = d.manufacturer_id
            LEFT JOIN device_types dt ON dt.id = d.type_id
            WHERE dt.code=?
            ORDER BY manufacturer, model
            """,
            (type_code,),
        )
    else:
        cur.execute(
            """
            SELECT d.id, m.name AS manufacturer, dt.code AS type, d.model, d.name, d.symbol
            FROM devices d
            LEFT JOIN manufacturers m ON m.id = d.manufacturer_id
            LEFT JOIN device_types dt ON dt.id = d.type_id
            ORDER BY manufacturer, model
            """
        )
    rows = [dict(r) for r in cur.fetchall()]
    con.close()
    return rows


def get_device_specs(device_id: int) -> Optional[Dict[str, Any]]:
    con = _connect(); cur = con.cursor()
    cur.execute(
        "SELECT strobe_candela, speaker_db_at10ft, smoke_spacing_ft, current_a, voltage_v, notes FROM device_specs WHERE device_id=?",
        (device_id,),
    )
    row = cur.fetchone(); con.close()
    if not row:
        return None
    return dict(row)

