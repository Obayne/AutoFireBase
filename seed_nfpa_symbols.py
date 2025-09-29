#!/usr/bin/env python3
"""
NFPA 170 Symbol Seeder

Adds standardized NFPA 170 fire safety and emergency symbols to the AutoFire catalog.
NFPA 170 provides standardized symbols for fire safety equipment and emergency communications.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any

from backend.catalog_store import _connect


def get_nfpa_170_symbols() -> list[dict[str, Any]]:
    """Return comprehensive list of NFPA 170 symbols with metadata."""
    return [
        # Fire Extinguishers
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "FIRE_EXT_ABC",
            "name": "Fire Extinguisher (ABC)",
            "symbol": "🔥ABC",  # Placeholder - will be replaced with proper symbol
            "specs": {
                "symbol_type": "fire_extinguisher",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "red",
                "notes": "ABC dry chemical fire extinguisher"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "FIRE_EXT_CO2",
            "name": "Fire Extinguisher (CO2)",
            "symbol": "🔥CO2",
            "specs": {
                "symbol_type": "fire_extinguisher",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "red",
                "notes": "Carbon dioxide fire extinguisher"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "FIRE_EXT_WATER",
            "name": "Fire Extinguisher (Water)",
            "symbol": "🔥H2O",
            "specs": {
                "symbol_type": "fire_extinguisher",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "red",
                "notes": "Water-based fire extinguisher"
            }
        },

        # Exit Signs
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "EXIT_SIGN",
            "name": "Exit Sign",
            "symbol": "EXIT",
            "specs": {
                "symbol_type": "exit_sign",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "green",
                "illuminated": True,
                "notes": "Standard exit sign with directional arrow"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "EXIT_LEFT",
            "name": "Exit Left Arrow",
            "symbol": "←EXIT",
            "specs": {
                "symbol_type": "exit_sign",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "green",
                "direction": "left",
                "notes": "Exit sign with left directional arrow"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "EXIT_RIGHT",
            "name": "Exit Right Arrow",
            "symbol": "EXIT→",
            "specs": {
                "symbol_type": "exit_sign",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "green",
                "direction": "right",
                "notes": "Exit sign with right directional arrow"
            }
        },

        # Emergency Equipment
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "EYEWASH_STATION",
            "name": "Eyewash Station",
            "symbol": "👁💧",
            "specs": {
                "symbol_type": "emergency_equipment",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "green",
                "notes": "Emergency eyewash station"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "SAFETY_SHOWER",
            "name": "Safety Shower",
            "symbol": "🚿",
            "specs": {
                "symbol_type": "emergency_equipment",
                "nfpa_standard": "170",
                "min_size_inches": 6,
                "color": "green",
                "notes": "Emergency safety shower"
            }
        },

        # Fire Alarm Devices
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "FIRE_ALARM_PULL",
            "name": "Fire Alarm Pull Station",
            "symbol": "🔴PULL",
            "specs": {
                "symbol_type": "fire_alarm_device",
                "nfpa_standard": "170",
                "min_size_inches": 4,
                "color": "red",
                "notes": "Manual fire alarm pull station"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "FIRE_HORN",
            "name": "Fire Horn",
            "symbol": "📣",
            "specs": {
                "symbol_type": "fire_alarm_device",
                "nfpa_standard": "170",
                "min_size_inches": 4,
                "color": "red",
                "notes": "Fire alarm notification horn"
            }
        },

        # Safety Markings
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "NO_SMOKING",
            "name": "No Smoking",
            "symbol": "🚭",
            "specs": {
                "symbol_type": "safety_marking",
                "nfpa_standard": "170",
                "min_size_inches": 8,
                "color": "red",
                "notes": "No smoking area designation"
            }
        },
        {
            "manufacturer": "NFPA",
            "type_code": "NFPA 170",
            "model": "HAZARD_CHEMICAL",
            "name": "Chemical Hazard",
            "symbol": "☠⚗",
            "specs": {
                "symbol_type": "safety_marking",
                "nfpa_standard": "170",
                "min_size_inches": 8,
                "color": "yellow_black",
                "notes": "Chemical hazard warning"
            }
        }
    ]


def seed_nfpa_symbols():
    """Add NFPA 170 symbols to the main database."""
    con = sqlite3.connect("autofire.db")
    cur = con.cursor()

    # Ensure NFPA device type exists
    cur.execute(
        "INSERT OR IGNORE INTO device_types(code, description) VALUES(?,?)",
        ("NFPA 170", "NFPA 170 Fire Safety Symbols")
    )

    symbols = get_nfpa_170_symbols()

    for symbol_data in symbols:
        try:
            # Get manufacturer ID
            cur.execute("INSERT OR IGNORE INTO manufacturers(name) VALUES(?)", (symbol_data["manufacturer"],))
            cur.execute("SELECT id FROM manufacturers WHERE name=?", (symbol_data["manufacturer"],))
            manufacturer_id = cur.fetchone()[0]

            # Get type ID
            cur.execute("SELECT id FROM device_types WHERE code=?", (symbol_data["type_code"],))
            type_row = cur.fetchone()
            if not type_row:
                print(f"Warning: Device type {symbol_data['type_code']} not found, skipping {symbol_data['name']}")
                continue
            type_id = type_row[0]

            # Check if symbol already exists
            cur.execute(
                "SELECT id FROM devices WHERE manufacturer_id=? AND model=?",
                (manufacturer_id, symbol_data["model"])
            )
            existing = cur.fetchone()

            if existing:
                # Update existing symbol
                properties = json.dumps(symbol_data.get("specs", {}))
                cur.execute(
                    "UPDATE devices SET type_id=?, name=?, symbol=?, properties_json=? WHERE id=?",
                    (
                        type_id,
                        symbol_data["name"],
                        symbol_data["symbol"],
                        properties,
                        existing[0]
                    )
                )
                print(f"Updated NFPA symbol: {symbol_data['name']}")
                continue

            # Add device
            properties = json.dumps(symbol_data.get("specs", {}))
            cur.execute(
                "INSERT INTO devices(manufacturer_id, type_id, model, name, symbol, properties_json) VALUES(?,?,?,?,?,?)",
                (
                    manufacturer_id,
                    type_id,
                    symbol_data["model"],
                    symbol_data["name"],
                    symbol_data["symbol"],
                    properties
                )
            )

            device_id = cur.lastrowid

            # Add specs if provided
            specs = symbol_data.get("specs", {})
            if specs:
                cur.execute(
                    "INSERT OR REPLACE INTO device_specs(device_id, notes) VALUES(?,?)",
                    (device_id, specs.get("notes", ""))
                )

            print(f"Added NFPA symbol: {symbol_data['name']}")

        except Exception as e:
            print(f"Error adding symbol {symbol_data['name']}: {e}")
            continue

    con.commit()
    con.close()
    print("NFPA 170 symbol seeding completed")


if __name__ == "__main__":
    seed_nfpa_symbols()
