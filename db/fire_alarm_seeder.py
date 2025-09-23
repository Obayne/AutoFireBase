"""
Database seeder for Fire-Lite devices and enhanced schema for fire alarm systems.
Adds Fire-Lite manufacturer and devices to the existing catalog database.
"""

import sqlite3
import json
from typing import Dict, Any
from .firelite_catalog import FIRELITE_CATALOG
from .schema import ensure_db


def enhance_fire_alarm_schema(con: sqlite3.Connection):
    """Enhance database schema to support fire alarm system design."""
    cur = con.cursor()
    
    # Add SLC (Signaling Line Circuit) tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS slc_circuits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panel_device_id INTEGER,
            loop_number INTEGER,
            max_devices INTEGER DEFAULT 159,
            wire_type TEXT DEFAULT 'FPLR',
            wire_gauge TEXT DEFAULT '18 AWG',
            supervision_type TEXT DEFAULT 'Class A',
            FOREIGN KEY(panel_device_id) REFERENCES devices(id),
            UNIQUE(panel_device_id, loop_number)
        )
    """)
    
    # Device addressing and connections
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_device_id INTEGER,
            slc_circuit_id INTEGER,
            device_address INTEGER,
            device_type_code TEXT,
            x_coordinate REAL,
            y_coordinate REAL,
            floor_level TEXT DEFAULT 'Ground',
            zone_description TEXT,
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(slc_circuit_id) REFERENCES slc_circuits(id),
            UNIQUE(slc_circuit_id, device_address)
        )
    """)
    
    # Circuit calculations and electrical data
    cur.execute("""
        CREATE TABLE IF NOT EXISTS circuit_calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slc_circuit_id INTEGER,
            total_standby_current REAL DEFAULT 0.0,
            total_alarm_current REAL DEFAULT 0.0,
            wire_length_feet REAL DEFAULT 0.0,
            voltage_drop_percent REAL DEFAULT 0.0,
            power_limited BOOLEAN DEFAULT TRUE,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(slc_circuit_id) REFERENCES slc_circuits(id)
        )
    """)
    
    # Wire connections for visualization and documentation
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_device_address_id INTEGER,
            to_device_address_id INTEGER,
            connection_type TEXT DEFAULT 'SLC',
            wire_path_json TEXT,
            length_feet REAL DEFAULT 0.0,
            FOREIGN KEY(from_device_address_id) REFERENCES device_addresses(id),
            FOREIGN KEY(to_device_address_id) REFERENCES device_addresses(id)
        )
    """)
    
    # Project panels for tracking which panels are used in each project
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_panels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            device_id INTEGER,
            panel_name TEXT,
            x_coordinate REAL,
            y_coordinate REAL,
            floor_level TEXT DEFAULT 'Ground',
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
    """)
    
    # Enhanced device specs for fire alarm calculations
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fire_alarm_specs (
            device_id INTEGER PRIMARY KEY,
            current_standby_ma REAL DEFAULT 0.0,
            current_alarm_ma REAL DEFAULT 0.0,
            voltage_nominal REAL DEFAULT 24.0,
            addressable BOOLEAN DEFAULT FALSE,
            slc_compatible BOOLEAN DEFAULT FALSE,
            spacing_feet REAL DEFAULT 30.0,
            candela_rating INTEGER,
            sound_level_db INTEGER,
            detector_type TEXT,
            thermal_rating INTEGER,
            ul_category TEXT,
            installation_notes TEXT,
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )
    """)
    
    # Layer management for fire alarm vs architectural separation
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fire_alarm_layers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            layer_name TEXT UNIQUE NOT NULL,
            layer_type TEXT,  -- 'fire_alarm', 'architectural', 'electrical', 'mechanical'
            color_rgb TEXT DEFAULT '#FF0000',
            line_weight INTEGER DEFAULT 1,
            visible BOOLEAN DEFAULT TRUE,
            printable BOOLEAN DEFAULT TRUE,
            description TEXT
        )
    """)
    
    con.commit()


def seed_fire_alarm_layers(con: sqlite3.Connection):
    """Seed standard fire alarm layers."""
    cur = con.cursor()
    
    layers = [
        ("FA-DEVICES", "fire_alarm", "#FF0000", 2, "Fire alarm devices"),
        ("FA-WIRING", "fire_alarm", "#FF4444", 1, "Fire alarm wiring and connections"),
        ("FA-ZONES", "fire_alarm", "#FF8888", 1, "Fire alarm zones and areas"),
        ("FA-PANELS", "fire_alarm", "#CC0000", 3, "Fire alarm control panels"),
        ("FA-RISER", "fire_alarm", "#990000", 2, "Riser diagram elements"),
        ("FA-NOTES", "fire_alarm", "#660000", 1, "Fire alarm notes and labels"),
        ("A-WALL", "architectural", "#000000", 2, "Architectural walls"),
        ("A-DOOR", "architectural", "#004400", 1, "Doors and openings"),
        ("A-FLOR", "architectural", "#444444", 1, "Floor plan elements"),
        ("E-POWER", "electrical", "#0000FF", 1, "Electrical power"),
        ("M-HVAC", "mechanical", "#00AA00", 1, "HVAC systems")
    ]
    
    for layer_name, layer_type, color, weight, desc in layers:
        cur.execute("""
            INSERT OR IGNORE INTO fire_alarm_layers 
            (layer_name, layer_type, color_rgb, line_weight, description) 
            VALUES (?, ?, ?, ?, ?)
        """, (layer_name, layer_type, color, weight, desc))
    
    con.commit()


def seed_firelite_devices(con: sqlite3.Connection):
    """Populate database with Fire-Lite device catalog."""
    cur = con.cursor()
    
    # Ensure Fire-Lite manufacturer exists
    cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES(?)", ("Fire-Lite",))
    cur.execute("SELECT id FROM manufacturers WHERE name=?", ("Fire-Lite",))
    firelite_id = cur.fetchone()[0]
    
    # Ensure device types exist
    device_types = [
        ("FACP", "Fire Alarm Control Panel"),
        ("Detector", "Smoke/Heat/Multi-Sensor Detectors"), 
        ("Notification", "Strobes/Horn-Strobes/Speakers"),
        ("Initiating", "Manual Pull Stations"),
        ("Module", "Input/Output Control Modules")
    ]
    
    for code, desc in device_types:
        cur.execute("INSERT OR IGNORE INTO device_types(code, description) VALUES(?, ?)", (code, desc))
    
    # Get type IDs
    type_ids = {}
    for code, _ in device_types:
        cur.execute("SELECT id FROM device_types WHERE code=?", (code,))
        type_ids[code] = cur.fetchone()[0]
    
    # Insert Fire-Lite devices
    devices_added = 0
    for model, spec in FIRELITE_CATALOG.items():
        device_type = spec.get("type", "Unknown")
        type_id = type_ids.get(device_type)
        
        if not type_id:
            print(f"Warning: Unknown device type '{device_type}' for {model}")
            continue
            
        # Create device record
        properties = {k: v for k, v in spec.items() if k not in ["name", "description", "type"]}
        
        cur.execute("""
            INSERT OR IGNORE INTO devices 
            (manufacturer_id, type_id, model, name, symbol, properties_json) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            firelite_id,
            type_id, 
            model,
            spec.get("name", model),
            _get_device_symbol(spec),
            json.dumps(properties)
        ))
        
        # Get device ID for additional specs
        cur.execute("SELECT id FROM devices WHERE manufacturer_id=? AND model=?", (firelite_id, model))
        device_row = cur.fetchone()
        if device_row:
            device_id = device_row[0]
            
            # Add fire alarm specific specs
            cur.execute("""
                INSERT OR REPLACE INTO fire_alarm_specs (
                    device_id, current_standby_ma, current_alarm_ma, voltage_nominal,
                    addressable, slc_compatible, spacing_feet, candela_rating,
                    sound_level_db, detector_type, thermal_rating, ul_category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                device_id,
                spec.get("current_standby", 0.0) * 1000,  # Convert to mA
                spec.get("current_alarm", 0.0) * 1000,    # Convert to mA  
                spec.get("voltage", 24.0),
                spec.get("addressable", False),
                spec.get("addressable", False),  # SLC compatible if addressable
                spec.get("spacing_standard", 30.0),
                _get_candela_rating(spec),
                _get_sound_level(spec),
                spec.get("detection_type"),
                spec.get("thermal_rating"),
                "Fire Alarm"
            ))
            
            devices_added += 1
    
    con.commit()
    return devices_added


def _get_device_symbol(spec: Dict[str, Any]) -> str:
    """Generate appropriate symbol for device type."""
    device_type = spec.get("type", "")
    detection_type = spec.get("detection_type", "")
    notification_type = spec.get("notification_type", "")
    
    if device_type == "FACP":
        return "FACP"
    elif device_type == "Detector":
        if "photoelectric" in detection_type:
            return "SD"  # Smoke Detector
        elif "thermal" in detection_type:
            return "HD"  # Heat Detector  
        else:
            return "DET"
    elif device_type == "Notification":
        if notification_type == "visual":
            return "STR"  # Strobe
        elif notification_type == "audible_visual":
            return "HS"   # Horn Strobe
        elif notification_type == "voice_visual":
            return "SPK"  # Speaker
        else:
            return "NOT"
    elif device_type == "Initiating":
        return "PS"  # Pull Station
    elif device_type == "Module":
        return "MOD"
    else:
        return "DEV"


def _get_candela_rating(spec: Dict[str, Any]) -> int | None:
    """Extract candela rating from device spec."""
    candela_options = spec.get("candela_options", [])
    if candela_options:
        return candela_options[0]  # Return lowest rating as default
    return None


def _get_sound_level(spec: Dict[str, Any]) -> int | None:
    """Extract sound level from device spec.""" 
    sound_output = spec.get("sound_output", {})
    if isinstance(sound_output, dict):
        return sound_output.get("med", sound_output.get("high", None))
    return None


def initialize_fire_alarm_database(db_path: str | None = None):
    """Initialize complete fire alarm database with Fire-Lite catalog."""
    # Ensure base schema exists
    ensure_db(db_path or "catalog.db")
    
    # Connect and enhance
    con = sqlite3.connect(db_path or "catalog.db")
    con.row_factory = sqlite3.Row
    
    try:
        enhance_fire_alarm_schema(con)
        seed_fire_alarm_layers(con)
        devices_added = seed_firelite_devices(con)
        
        print(f"Fire alarm database initialized successfully!")
        print(f"Added {devices_added} Fire-Lite devices to catalog")
        
        return True
        
    except Exception as e:
        print(f"Error initializing fire alarm database: {e}")
        return False
    finally:
        con.close()


if __name__ == "__main__":
    # Test the database initialization
    initialize_fire_alarm_database()