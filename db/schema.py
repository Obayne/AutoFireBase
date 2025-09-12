
# Minimal scaffolding for future SQLite catalog (not wired yet)
import sqlite3, os
from pathlib import Path

def ensure_db(path: str):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS manufacturers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS device_types(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        description TEXT
    );
    """)
    cur.execute("""
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
    """)
    # Optional structured specs for common calculations
    cur.execute("""
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
    """)
    con.commit(); con.close()
