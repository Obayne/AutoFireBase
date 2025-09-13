from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from db import loader


@dataclass
class Device:
    name: str
    symbol: str
    type: str
    manufacturer: str
    part_number: str


class CatalogStore:
    """Thin wrapper around the SQLite catalog with a stable API.

    Keeps all persistence details in one spot and exposes simple
    list/search and insert helpers for the frontend/backend.
    """

    def __init__(self, db_path: str | Path, *, seed_demo: bool = False) -> None:
        self.db_path = str(db_path)
        self.con = loader.connect(self.db_path)
        loader.ensure_schema(self.con)
        if seed_demo:
            loader.seed_demo(self.con)

    def close(self) -> None:
        try:
            self.con.close()
        except Exception:
            pass

    # Discovery
    def list_types(self) -> List[str]:
        return loader.list_types(self.con)

    def list_manufacturers(self) -> List[str]:
        return loader.list_manufacturers(self.con)

    def list_devices(self, *, type_filter: Optional[str] = None, query: Optional[str] = None) -> List[Device]:
        rows = loader.fetch_devices(self.con)
        out: List[Device] = []
        for r in rows:
            if type_filter and r.get("type") != type_filter:
                continue
            if query:
                q = query.lower()
                if q not in (r.get("name", "").lower()) and q not in (r.get("part_number", "").lower()):
                    continue
            out.append(Device(**r))
        return out

    def strobe_radius_for_candela(self, candela: int) -> Optional[float]:
        return loader.strobe_radius_for_candela(self.con, int(candela))

    # Mutations
    def add_device(
        self,
        *,
        manufacturer: str,
        type_code: str,
        model: str,
        name: str,
        symbol: str,
        props: Optional[Dict[str, Any]] = None,
    ) -> int:
        cur = self.con.cursor()
        # ensure foreign keys
        cur.execute("SELECT id FROM manufacturers WHERE name=?", (manufacturer,))
        row = cur.fetchone()
        if row:
            m_id = row[0]
        else:
            cur.execute("INSERT INTO manufacturers(name) VALUES(?)", (manufacturer,))
            m_id = cur.lastrowid

        cur.execute("SELECT id FROM device_types WHERE code=?", (type_code,))
        row = cur.fetchone()
        if row:
            t_id = row[0]
        else:
            cur.execute("INSERT INTO device_types(code) VALUES(?)", (type_code,))
            t_id = cur.lastrowid

        cur.execute(
            "INSERT INTO devices(manufacturer_id,type_id,model,name,symbol,properties_json) VALUES(?,?,?,?,?,?)",
            (m_id, t_id, model, name, symbol, json.dumps(props or {})),
        )
        self.con.commit()
        return int(cur.lastrowid)

