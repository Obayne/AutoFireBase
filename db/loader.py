import os, sqlite3, json
from pathlib import Path

DB_DEFAULT = os.path.join(os.path.expanduser('~'), 'AutoFire', 'catalog.db')

def connect(db_path: str = None):
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
        CREATE TABLE IF NOT EXISTS strobe_candela(
            candela INTEGER PRIMARY KEY,
            radius_ft REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS smoke_spacing(
            ceiling_height_ft REAL,
            spacing_ft REAL,
            PRIMARY KEY (ceiling_height_ft)
        );
        """
    )
    con.commit()

def _id_for(cur, table, key, value):
    cur.execute(f"SELECT id FROM {table} WHERE {key}=?", (value,))
    row = cur.fetchone()
    if row:
        return row['id']
    cur.execute(f"INSERT INTO {table}({key}) VALUES(?)", (value,))
    return cur.lastrowid

def seed_demo(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM devices")
    if cur.fetchone()['c'] > 0:
        return
    types = {
        'Detector': 'Smokes/Heat',
        'Notification': 'Strobes/HornStrobes/Speakers',
        'Initiating': 'Pulls/Manual',
    }
    for code, desc in types.items():
        _id_for(cur, 'device_types', 'code', code)
    mfr_id = _id_for(cur, 'manufacturers', 'name', '(Any)')
    def add(dev):
        t_id = _id_for(cur, 'device_types', 'code', dev['type'])
        cur.execute(
            "INSERT INTO devices(manufacturer_id,type_id,model,name,symbol,properties_json) VALUES(?,?,?,?,?,?)",
            (mfr_id, t_id, dev.get('part_number',''), dev['name'], dev['symbol'], json.dumps(dev.get('props',{})))
        )
    demo = [
        {"name":"Smoke Detector", "symbol":"SD", "type":"Detector", "part_number":"GEN-SD"},
        {"name":"Heat Detector",  "symbol":"HD", "type":"Detector", "part_number":"GEN-HD"},
        {"name":"Strobe",         "symbol":"S",  "type":"Notification", "part_number":"GEN-S",
         "props":{"candelas":[15,30,75,95,110,135,185]}},
        {"name":"Horn Strobe",    "symbol":"HS", "type":"Notification", "part_number":"GEN-HS",
         "props":{"candelas":[15,30,75,95,110,135,185]}},
        {"name":"Speaker",        "symbol":"SPK","type":"Notification", "part_number":"GEN-SPK"},
        {"name":"Pull Station",   "symbol":"PS", "type":"Initiating", "part_number":"GEN-PS"},
    ]
    for d in demo:
        add(d)
    # seed candela mapping (rough placeholders)
    cur.executemany("INSERT OR IGNORE INTO strobe_candela(candela,radius_ft) VALUES(?,?)",
                    [(15,15.0),(30,20.0),(75,30.0),(95,35.0),(110,38.0),(135,43.0),(185,50.0)])
    # seed smoke spacing (placeholder: single height)
    cur.execute("INSERT OR IGNORE INTO smoke_spacing(ceiling_height_ft, spacing_ft) VALUES(?,?)", (10.0, 30.0))
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

def strobe_radius_for_candela(con: sqlite3.Connection, cand: int) -> float | None:
    cur = con.cursor(); cur.execute("SELECT radius_ft FROM strobe_candela WHERE candela=?", (int(cand),))
    r = cur.fetchone()
    return float(r['radius_ft']) if r else None

def list_manufacturers(con: sqlite3.Connection):
    cur = con.cursor(); cur.execute("SELECT name FROM manufacturers ORDER BY name")
    return ['(Any)'] + [r['name'] for r in cur.fetchall()]

def list_types(con: sqlite3.Connection):
    cur = con.cursor(); cur.execute("SELECT code FROM device_types ORDER BY code")
    return ['(Any)'] + [r['code'] for r in cur.fetchall()]
