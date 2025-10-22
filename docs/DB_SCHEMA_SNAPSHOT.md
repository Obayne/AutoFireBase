# AutoFire DB Schema Snapshot (2025-10-05)

This document captures the current SQLite schema in `autofire.db` to reference during the rebuild.

Source: Introspected via PRAGMA from the live DB.

## Tables

- manufacturers
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL

- device_types
  - id INTEGER PRIMARY KEY
  - code TEXT NOT NULL
  - description TEXT

- devices
  - id INTEGER PRIMARY KEY
  - manufacturer_id INTEGER → manufacturers(id)
  - type_id INTEGER → device_types(id)
  - model TEXT
  - name TEXT
  - symbol TEXT
  - properties_json TEXT

- device_specs
  - device_id INTEGER PRIMARY KEY → devices(id)
  - strobe_candela REAL
  - speaker_db_at10ft REAL
  - smoke_spacing_ft REAL
  - current_a REAL
  - voltage_v REAL
  - notes TEXT

- panels
  - id INTEGER PRIMARY KEY
  - manufacturer_id INTEGER → manufacturers(id)
  - model TEXT NOT NULL
  - name TEXT
  - panel_type TEXT            // e.g., "main", "nac_booster", "power_supply"
  - max_devices INTEGER
  - properties_json TEXT

- panel_circuits
  - id INTEGER PRIMARY KEY
  - panel_id INTEGER → panels(id)
  - circuit_type TEXT          // e.g., SLC, NAC, RS-485
  - circuit_number INTEGER
  - max_devices INTEGER        // for SLC
  - max_current_a REAL         // for NAC/power
  - voltage_v REAL             // for NAC/power
  - properties_json TEXT

- panel_compatibility
  - id INTEGER PRIMARY KEY
  - panel_id INTEGER → panels(id)
  - device_type_id INTEGER → device_types(id)
  - compatible BOOLEAN DEFAULT 1
  - notes TEXT

- wires
  - id INTEGER PRIMARY KEY
  - manufacturer_id INTEGER → manufacturers(id)
  - type_id INTEGER → wire_types(id)
  - gauge INTEGER
  - color TEXT
  - insulation TEXT
  - ohms_per_1000ft REAL
  - max_current_a REAL
  - model TEXT
  - name TEXT
  - properties_json TEXT

- wire_types
  - id INTEGER PRIMARY KEY
  - code TEXT NOT NULL
  - description TEXT

- strobe_candela
  - candela INTEGER PRIMARY KEY
  - radius_ft REAL NOT NULL

- ceiling_strobe_coverage
  - ceiling_height INTEGER PRIMARY KEY
  - room_size INTEGER PRIMARY KEY
  - candela INTEGER NOT NULL

- wall_strobe_coverage
  - room_size INTEGER PRIMARY KEY
  - candela INTEGER NOT NULL

- sqlite_sequence (SQLite internal for AUTOINCREMENT)

## Relationships

- devices.manufacturer_id → manufacturers.id
- devices.type_id → device_types.id
- device_specs.device_id → devices.id
- panels.manufacturer_id → manufacturers.id
- panel_circuits.panel_id → panels.id
- panel_compatibility.panel_id → panels.id
- panel_compatibility.device_type_id → device_types.id
- wires.manufacturer_id → manufacturers.id
- wires.type_id → wire_types.id

## Notes for Rebuild

- Manufacturer normalization: canonical brand names (Fire-Lite Alarms, NOTIFIER, Gamewell-FCI, Silent Knight, System Sensor, Xtralis/VESDA). Consider adding a parent hierarchy to represent Honeywell umbrella while keeping brand-level identity.
- Panel types: ensure clear segregation of main panels vs NAC boosters vs power supplies vs annunciators; UI and DB should reflect this via `panel_type` and possibly a dedicated table or enum.
- JSON columns: `properties_json` used across entities; standardize keys and consider migration scripts for legacy formats.
- Coverage tables (strobe) currently modeled as simple lookup tables; verify alignment with NFPA signaling rules.

Generated: 2025-10-05
