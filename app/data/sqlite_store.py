import json
import os
import sqlite3

# SQL strings can be long and are clearer on one line; allow E501 for this file.
# ruff: noqa: E501
# noqa: E501
from .iface import DeviceRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS catalog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, symbol TEXT, manufacturer TEXT, part_number TEXT, type TEXT, attributes TEXT
);
CREATE TABLE IF NOT EXISTS project_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    data TEXT
);
"""


class SQLiteStore:
    def __init__(self, path: str):
        self.path = path
        self._ensure()

    def _ensure(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.executescript(SCHEMA)

    # ---- Catalog ----
    def upsert_catalog(self, items: list[DeviceRecord]):
        with sqlite3.connect(self.path) as db:
            for d in items:
                db.execute(
                    "INSERT INTO catalog (name, symbol, manufacturer, part_number, type, attributes) VALUES (?,?,?,?,?,?)",
                    (
                        d.name,
                        d.symbol,
                        d.manufacturer,
                        d.part_number,
                        d.type,
                        json.dumps(d.attributes or {}),
                    ),
                )
            db.commit()

    def list_catalog(self) -> list[DeviceRecord]:
        rows = []
        with sqlite3.connect(self.path) as db:
            cur = db.execute(
                "SELECT id, name, symbol, manufacturer, part_number, type, attributes FROM catalog ORDER BY name"
            )
            rows = cur.fetchall()
        out = []
        for id_, name, symbol, manufacturer, part_number, type_, attrs in rows:
            out.append(
                DeviceRecord(
                    id=id_,
                    name=name,
                    symbol=symbol,
                    manufacturer=manufacturer,
                    part_number=part_number,
                    type=type_,
                    attributes=json.loads(attrs or "{}"),
                )
            )
        return out

    # ---- Project snapshots ----
    def save_snapshot(self, data: dict):
        with sqlite3.connect(self.path) as db:
            db.execute("INSERT INTO project_snapshots (data) VALUES (?)", (json.dumps(data),))
            db.commit()

    def latest_snapshot(self) -> dict | None:
        with sqlite3.connect(self.path) as db:
            row = db.execute(
                "SELECT data FROM project_snapshots ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if not row:
                return None
            return json.loads(row[0])
