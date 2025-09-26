import json
import os
import sqlite3
from pathlib import Path

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
        CREATE TABLE IF NOT EXISTS system_categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS devices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer_id INTEGER,
            type_id INTEGER,
            category_id INTEGER,
            layer_id INTEGER,
            circuit_id INTEGER,
            model TEXT,
            name TEXT,
            symbol TEXT,
            properties_json TEXT,
            panel_standby_current_ma REAL, -- New: for FACP panel battery calculations
            panel_alarm_current_ma REAL,    -- New: for FACP panel battery calculations
            FOREIGN KEY(manufacturer_id) REFERENCES manufacturers(id),
            FOREIGN KEY(type_id) REFERENCES device_types(id),
            FOREIGN KEY(category_id) REFERENCES system_categories(id)
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
        -- Fire Alarm specific tables
        CREATE TABLE IF NOT EXISTS fire_alarm_device_specs(
            device_id INTEGER PRIMARY KEY,
            device_class TEXT, -- Detector, Notification, Initiating, Control
            max_current_ma REAL,
            standby_current_ma REAL, -- New: for battery calculations
            alarm_current_ma REAL,   -- New: for battery calculations
            voltage_v REAL,
            slc_compatible BOOLEAN,
            nac_compatible BOOLEAN,
            addressable BOOLEAN,
            candela_options TEXT, -- JSON array of available candela values
            FOREIGN KEY(device_id) REFERENCES devices(id)
        );
        CREATE TABLE IF NOT EXISTS wire_specs(
            gauge TEXT PRIMARY KEY, -- e.g., '18/2', '16/2'
            resistance_per_1000ft REAL NOT NULL -- Ohms per 1000 feet
        );
        CREATE TABLE IF NOT EXISTS circuits(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_id INTEGER, -- FACP panel this circuit belongs to
            circuit_type TEXT NOT NULL, -- e.g., 'SLC', 'NAC'
            capacity INTEGER, -- Max devices or length
            FOREIGN KEY(panel_id) REFERENCES devices(id)
        );
        -- CAD Block integration table
        CREATE TABLE IF NOT EXISTS cad_blocks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            block_name TEXT,
            block_path TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(id)
        );
        CREATE TABLE IF NOT EXISTS job_info(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            project_address TEXT,
            sheet_number TEXT,
            drawing_date TEXT,
            drawn_by TEXT
        );
        CREATE TABLE IF NOT EXISTS wires(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_number TEXT,
            manufacturer TEXT,
            type TEXT,
            gauge TEXT,
            color TEXT
        );
        CREATE TABLE IF NOT EXISTS layers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT,
            visible BOOLEAN,
            locked BOOLEAN,
            show_name BOOLEAN,
            show_part_number BOOLEAN,
            show_slc_address BOOLEAN,
            show_circuit_id BOOLEAN,
            show_zone BOOLEAN,
            show_max_current_ma BOOLEAN,
            show_voltage_v BOOLEAN,
            show_addressable BOOLEAN,
            show_candela_options BOOLEAN
        );
        """
    )
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

    # Fire alarm device types
    types = {
        "Detector": "Smokes/Heat",
        "Notification": "Strobes/HornStrobes/Speakers",
        "Initiating": "Pulls/Manual",
        "Control": "Fire Alarm Control Panels",
        "Sensor": "Security Sensors",
        "Camera": "CCTV Cameras",
        "Recorder": "Recording Devices",
    }

    # System categories
    categories = ["Fire Alarm", "Security", "CCTV", "Access Control"]

    for code, desc in types.items():
        _id_for(cur, "device_types", "code", code)

    for cat_name in categories:
        _id_for(cur, "system_categories", "name", cat_name)

    mfr_id = _id_for(cur, "manufacturers", "name", "(Any)")

    def add(dev):
        t_id = _id_for(cur, "device_types", "code", dev["type"])
        c_id = _id_for(cur, "system_categories", "name", dev.get("system_category", "Fire Alarm"))
        cur.execute(
            "INSERT INTO devices(manufacturer_id,type_id,category_id,layer_id,circuit_id,model,name,symbol,properties_json,panel_standby_current_ma,panel_alarm_current_ma) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                mfr_id,
                t_id,
                c_id,
                1,
                NULL,
                dev.get("part_number", ""),
                dev["name"],
                dev["symbol"],
                json.dumps(dev.get("props", {})),
                dev.get("panel_standby_current_ma", 0.0),
                dev.get("panel_alarm_current_ma", 0.0),
            ),
        )
        device_id = cur.lastrowid

        # Add fire alarm specific specs for fire alarm devices
        if dev.get("system_category", "Fire Alarm") == "Fire Alarm":
            specs = dev.get("specs", {})
            candela_options = json.dumps(specs.get("candela", [])) if specs.get("candela") else None

            cur.execute(
                """
                INSERT OR IGNORE INTO fire_alarm_device_specs 
                (device_id, device_class, max_current_ma, standby_current_ma, alarm_current_ma, voltage_v, slc_compatible, nac_compatible, addressable, candela_options)
                VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
                (
                    device_id,
                    dev["type"],
                    specs.get("max_current_ma", 0.0),
                    specs.get("standby_current_ma", 0.0),  # New
                    specs.get("alarm_current_ma", 0.0),  # New
                    specs.get("voltage_v", 0.0),
                    specs.get("slc_compatible", True),
                    specs.get("nac_compatible", True),
                    specs.get("addressable", True),
                    candela_options,
                ),
            )

    # Devices with enhanced specs and system categories
    demo = [
        {
            "name": "Smoke Detector",
            "symbol": "SD",
            "type": "Detector",
            "system_category": "Fire Alarm",
            "part_number": "GEN-SD",
            "specs": {
                "max_current_ma": 0.3,
                "standby_current_ma": 0.05,  # Example
                "alarm_current_ma": 0.3,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": False,
                "addressable": True,
            },
        },
        {
            "name": "Heat Detector",
            "symbol": "HD",
            "type": "Detector",
            "system_category": "Fire Alarm",
            "part_number": "GEN-HD",
            "specs": {
                "max_current_ma": 0.3,
                "standby_current_ma": 0.05,  # Example
                "alarm_current_ma": 0.3,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": False,
                "addressable": True,
            },
        },
        {
            "name": "Strobe",
            "symbol": "S",
            "type": "Notification",
            "system_category": "Fire Alarm",
            "part_number": "GEN-S",
            "specs": {
                "max_current_ma": 2.0,
                "standby_current_ma": 0.0,  # Example
                "alarm_current_ma": 2.0,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": True,
                "addressable": True,
            },
            "props": {"candelas": [15, 30, 75, 95, 110, 135, 185]},
        },
        {
            "name": "Horn Strobe",
            "symbol": "HS",
            "type": "Notification",
            "system_category": "Fire Alarm",
            "part_number": "GEN-HS",
            "specs": {
                "max_current_ma": 3.5,
                "standby_current_ma": 0.0,  # Example
                "alarm_current_ma": 3.5,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": True,
                "addressable": True,
            },
            "props": {"candelas": [15, 30, 75, 95, 110, 135, 185]},
        },
        {
            "name": "Speaker",
            "symbol": "SPK",
            "type": "Notification",
            "system_category": "Fire Alarm",
            "part_number": "GEN-SPK",
            "specs": {
                "max_current_ma": 1.0,
                "standby_current_ma": 0.0,  # Example
                "alarm_current_ma": 1.0,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": True,
                "addressable": True,
            },
        },
        {
            "name": "Pull Station",
            "symbol": "PS",
            "type": "Initiating",
            "system_category": "Fire Alarm",
            "part_number": "GEN-PS",
            "specs": {
                "max_current_ma": 0.1,
                "standby_current_ma": 0.0,  # Example
                "alarm_current_ma": 0.1,  # Example
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": False,
                "addressable": True,
            },
        },
        {
            "name": "FACP Panel",
            "symbol": "FACP",
            "type": "Control",
            "system_category": "Fire Alarm",
            "part_number": "GEN-FACP",
            "specs": {
                "max_current_ma": 0.0,  # Panel draws from AC power
                "voltage_v": 24.0,
                "slc_compatible": True,
                "nac_compatible": True,
                "addressable": False,  # Panel itself is not addressable
            },
            "panel_standby_current_ma": 100.0,  # Example
            "panel_alarm_current_ma": 500.0,  # Example
        },
        # Security Devices
        {
            "name": "Motion Detector",
            "symbol": "MD",
            "type": "Sensor",
            "system_category": "Security",
            "part_number": "GEN-MD",
        },
        {
            "name": "Door Contact",
            "symbol": "DC",
            "type": "Sensor",
            "system_category": "Security",
            "part_number": "GEN-DC",
        },
        # CCTV Devices
        {
            "name": "Camera",
            "symbol": "CAM",
            "type": "Camera",
            "system_category": "CCTV",
            "part_number": "GEN-CAM",
        },
        {
            "name": "DVR",
            "symbol": "DVR",
            "type": "Recorder",
            "system_category": "CCTV",
            "part_number": "GEN-DVR",
        },
    ]

    for d in demo:
        add(d)

    # seed candela mapping (rough placeholders)
    cur.executemany(
        "INSERT OR IGNORE INTO strobe_candela(candela,radius_ft) VALUES(?,?)",
        [(15, 15.0), (30, 20.0), (75, 30.0), (95, 35.0), (110, 38.0), (135, 43.0), (185, 50.0)],
    )

    # seed smoke spacing (placeholder: single height)
    cur.execute(
        "INSERT OR IGNORE INTO smoke_spacing(ceiling_height_ft, spacing_ft) VALUES(?,?)",
        (10.0, 30.0),
    )
    seed_wires(con)  # Call the new wire seeding function
    cur.execute(
        "INSERT OR IGNORE INTO layers (name, color, visible, locked, show_name, show_part_number) VALUES (?, ?, ?, ?, ?, ?)",
        ("0", "#FFFFFF", True, False, True, True),
    )

    # Seed wire specs (gauge to resistance per 1000ft)
    cur.executemany(
        "INSERT OR IGNORE INTO wire_specs(gauge, resistance_per_1000ft) VALUES(?,?)",
        [
            ("18/2", 6.38),  # Example for 18 AWG, 2 conductor
            ("16/2", 4.01),  # Example for 16 AWG, 2 conductor
            ("14/2", 2.52),  # Example for 14 AWG, 2 conductor
            ("12/2", 1.59),  # Example for 12 AWG, 2 conductor
        ],
    )
    con.commit()


def seed_wires(con: sqlite3.Connection):
    cur = con.cursor()
    wires = [
        ("5501", "Honeywell", "FPLP", "18/2", "Red"),
        ("5502", "Honeywell", "FPLP", "16/2", "Red"),
        ("5503", "Honeywell", "FPLP", "14/2", "Red"),
        ("6501", "Genesis", "CL3P", "18/2", "Black"),
        ("6502", "Genesis", "CL3P", "16/2", "Black"),
        ("6503", "Genesis", "CL3P", "14/2", "White"),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO wires(part_number, manufacturer, type, gauge, color) VALUES(?,?,?,?,?)",
        wires,
    )
    con.commit()


def fetch_devices(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.id, d.name, d.symbol, dt.code AS type, m.name AS manufacturer, d.model AS part_number, sc.name AS system_category, 
               fas.slc_compatible, fas.nac_compatible
        FROM devices d
        LEFT JOIN manufacturers m ON m.id=d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id=d.type_id
        LEFT JOIN system_categories sc ON sc.id=d.category_id
        LEFT JOIN fire_alarm_device_specs fas ON fas.device_id=d.id
        ORDER BY d.name
        """
    )
    return [dict(row) for row in cur.fetchall()]


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


def get_device_specs(con: sqlite3.Connection, device_id: int) -> dict:
    """Get fire alarm specific specifications for a device."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM fire_alarm_device_specs WHERE device_id = ?
    """,
        (device_id,),
    )

    row = cur.fetchone()
    if row:
        result = dict(row)
        # Parse JSON fields
        if result.get("candela_options"):
            try:
                result["candela_options"] = json.loads(result["candela_options"])
            except:
                result["candela_options"] = []
        return result
    return {}


def register_block_for_device(
    con: sqlite3.Connection,
    device_id: int,
    block_name: str,
    block_path: str,
    attributes: dict | None = None,
) -> int:
    """Register a CAD block for a specific device."""
    cur = con.cursor()
    attributes_json = json.dumps(attributes) if attributes else "{}"

    # Check if block already exists for this device
    cur.execute("SELECT id FROM cad_blocks WHERE device_id = ?", (device_id,))
    existing = cur.fetchone()

    if existing:
        # Update existing block registration
        cur.execute(
            """
            UPDATE cad_blocks 
            SET block_name = ?, block_path = ?, block_attributes = ?
            WHERE device_id = ?
        """,
            (block_name, block_path, attributes_json, device_id),
        )
    else:
        # Insert new block registration
        cur.execute(
            """
            INSERT INTO cad_blocks (device_id, block_name, block_path, block_attributes)
            VALUES (?, ?, ?, ?)
        """,
            (device_id, block_name, block_path, attributes_json),
        )

    con.commit()
    last_id = cur.lastrowid
    return last_id if last_id is not None else 0


def get_block_for_device(con: sqlite3.Connection, device_id: int) -> dict | None:
    """Get block information for a specific device."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT block_name, block_path, block_attributes
        FROM cad_blocks 
        WHERE device_id = ?
    """,
        (device_id,),
    )

    row = cur.fetchone()
    if row:
        result = {
            "block_name": row["block_name"],
            "block_path": row["block_path"],
            "block_attributes": (
                json.loads(row["block_attributes"]) if row["block_attributes"] else {}
            ),
        }
        return result
    return None


def fetch_devices_with_blocks(con: sqlite3.Connection) -> list:
    """Fetch devices with their associated block information."""
    cur = con.cursor()
    cur.execute(
        """
        SELECT d.id, d.name, d.symbol, dt.code AS type, m.name AS manufacturer, 
               d.model AS part_number, sc.name AS system_category,
               cb.block_name, cb.block_path
        FROM devices d
        LEFT JOIN manufacturers m ON m.id=d.manufacturer_id
        LEFT JOIN device_types dt ON dt.id=d.type_id
        LEFT JOIN system_categories sc ON sc.id=d.category_id
        LEFT JOIN cad_blocks cb ON cb.device_id=d.id
        ORDER BY d.name
        """
    )
    return [dict(row) for row in cur.fetchall()]


def fetch_wires(con: sqlite3.Connection) -> list:
    """Fetch all wire types from the database."""
    cur = con.cursor()
    cur.execute("SELECT * FROM wires ORDER BY manufacturer, type, gauge")
    return [dict(row) for row in cur.fetchall()]


def fetch_layers(con: sqlite3.Connection) -> list:
    """Fetch all layers from the database."""
    cur = con.cursor()
    cur.execute("SELECT * FROM layers ORDER BY name")
    return [dict(row) for row in cur.fetchall()]


def save_job_info(
    con: sqlite3.Connection,
    project_name: str,
    project_address: str,
    sheet_number: str,
    drawing_date: str,
    drawn_by: str,
):
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO job_info (id, project_name, project_address, sheet_number, drawing_date, drawn_by) VALUES (1, ?, ?, ?, ?, ?)",
        (project_name, project_address, sheet_number, drawing_date, drawn_by),
    )
    con.commit()


def fetch_job_info(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute("SELECT * FROM job_info WHERE id = 1")
    row = cur.fetchone()
    return dict(row) if row else {}


def save_circuit(
    con: sqlite3.Connection, panel_id: int, circuit_type: str, capacity: int, cable_length: float
):
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO circuits (panel_id, circuit_type, capacity, cable_length) VALUES (?, ?, ?, ?)",
        (panel_id, circuit_type, capacity, cable_length),
    )
    con.commit()


def fetch_circuit(con: sqlite3.Connection, panel_id: int):
    cur = con.cursor()
    cur.execute("SELECT * FROM circuits WHERE panel_id = ?", (panel_id,))
    row = cur.fetchone()
    return dict(row) if row else None


def fetch_layers(con: sqlite3.Connection) -> list:
    """Fetch all layers from the database."""
    cur = con.cursor()
    cur.execute("SELECT * FROM layers ORDER BY name")
    return [dict(row) for row in cur.fetchall()]
