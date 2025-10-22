"""
Transform and import data from artifacts/db_export_from_xls.db into autofire.db.
- Normalizes manufacturers to canonical brands
- Populates manufacturers, device_types, panels, and devices tables
- Heuristically assigns panel_type and properties_json
"""

import json
import os
import sqlite3

root = os.path.dirname(os.path.dirname(__file__))
source_db = os.path.join(root, "artifacts", "db_export_from_xls.db")
target_db = os.path.join(root, "autofire.db")

src = sqlite3.connect(source_db)
src.row_factory = sqlite3.Row
tgt = sqlite3.connect(target_db)
tgt.row_factory = sqlite3.Row
scur = src.cursor()
tcur = tgt.cursor()

# Manufacturer normalization
CANONICALS = [
    ("fire", "lite", "Fire-Lite Alarms"),
    ("notifier", None, "NOTIFIER"),
    ("gamewell", None, "Gamewell-FCI"),
    ("silent", "knight", "Silent Knight"),
    ("system sensor", None, "System Sensor"),
    ("vesda", None, "Xtralis/VESDA"),
    ("xtralis", None, "Xtralis/VESDA"),
]


def normalize_manufacturer(m):
    m = (m or "").strip()
    low = m.lower()
    for a, b, canon in CANONICALS:
        if a in low and (b is None or b in low):
            return canon
    return m


# Build manufacturers
manuf_map = {}
scur.execute(
    "SELECT DISTINCT Manufacturer FROM imported_panels_devices WHERE Manufacturer IS NOT NULL"
)
for row in scur.fetchall():
    m = row[0].strip()
    canon = normalize_manufacturer(m)
    tcur.execute("SELECT id FROM manufacturers WHERE name=?", (canon,))
    r = tcur.fetchone()
    if r:
        mid = r[0]
    else:
        tcur.execute("INSERT INTO manufacturers (name) VALUES (?)", (canon,))
        mid = tcur.lastrowid
    manuf_map[m] = mid

# Build device_types
scur.execute("SELECT DISTINCT PartType FROM imported_panels_devices WHERE PartType IS NOT NULL")
devtype_map = {}
for row in scur.fetchall():
    code = row[0].strip()
    tcur.execute("SELECT id FROM device_types WHERE code=?", (code,))
    r = tcur.fetchone()
    if r:
        tid = r[0]
    else:
        tcur.execute("INSERT INTO device_types (code) VALUES (?)", (code,))
        tid = tcur.lastrowid
    devtype_map[code] = tid

# Insert panels and devices
scur.execute(
    "SELECT * FROM imported_panels_devices WHERE Manufacturer IS NOT NULL AND Model IS NOT NULL"
)
rows = scur.fetchall()
for r in rows:
    m = r["Manufacturer"].strip()
    model = r["Model"]
    parttype = r["PartType"]
    desc = r["Description"]
    nomv = r["NominalVoltage"]
    minv = r["MinVoltage"]
    props = {"nominal_voltage": nomv, "min_voltage": minv, "description": desc}
    is_panel = parttype and ("panel" in parttype.lower() or "facp" in parttype.lower())
    if is_panel:
        tcur.execute(
            "SELECT id FROM panels WHERE model=? AND manufacturer_id=?", (model, manuf_map[m])
        )
        if not tcur.fetchone():
            tcur.execute(
                (
                    "INSERT INTO panels (manufacturer_id, model, name, panel_type, "
                    "max_devices, properties_json) VALUES (?, ?, ?, ?, ?, ?)"
                ),
                (manuf_map[m], model, desc, parttype, None, json.dumps(props)),
            )
    else:
        tcur.execute(
            "SELECT id FROM devices WHERE model=? AND manufacturer_id=?", (model, manuf_map[m])
        )
        if not tcur.fetchone():
            tcur.execute(
                (
                    "INSERT INTO devices (manufacturer_id, type_id, model, name, symbol, "
                    "properties_json) VALUES (?, ?, ?, ?, ?, ?)"
                ),
                (manuf_map[m], devtype_map.get(parttype), model, desc, None, json.dumps(props)),
            )
tgt.commit()
src.close()
tgt.close()
print("Import complete.")
