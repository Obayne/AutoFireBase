
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
    
    CREATE TABLE IF NOT EXISTS system_categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS circuits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        panel_id INTEGER,
        FOREIGN KEY(panel_id) REFERENCES devices(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS devices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manufacturer_id INTEGER,
        type_id INTEGER,
        category_id INTEGER,
        circuit_id INTEGER,
        model TEXT,
        name TEXT,
        symbol TEXT,
        properties_json TEXT,
        FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id),
        FOREIGN KEY(type_id) REFERENCES device_types(id),
        FOREIGN KEY(category_id) REFERENCES system_categories(id),
        FOREIGN KEY(circuit_id) REFERENCES circuits(id)
    );
    """)
    # Optional structured specs for common calculations
    CREATE TABLE IF NOT EXISTS device_specs(
        device_id INTEGER PRIMARY KEY,
        strobe_candela REAL,
        speaker_db_at10ft REAL,
        smoke_spacing_ft REAL,
        current_a REAL,
        voltage_v REAL,
        standby_current_ma REAL,
        alarm_current_ma REAL,
        notes TEXT,
        FOREIGN KEY(device_id) REFERENCES devices(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wire_specs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        manufacturer TEXT,
        type TEXT NOT NULL,
        gauge REAL NOT NULL,
        resistance_per_1000ft REAL,
        max_current_a REAL,
        notes TEXT
    );
    ")
    con.commit(); con.close()
