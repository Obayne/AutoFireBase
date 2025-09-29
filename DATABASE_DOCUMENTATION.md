# AutoFire Database Documentation

## Critical Database Files

### 🔴 autofire.db - MAIN APPLICATION DATABASE (CRITICAL - DO NOT DELETE)
**Location:** `c:\Dev\Autofire\autofire.db`
**Purpose:** Primary application database containing all device data and NFPA calculations
**Size:** ~14MB
**Tables:** 8 tables, 14,669 devices

#### Tables:
- **manufacturers** (168 rows): Device manufacturers
  - id (INTEGER, PK)
  - name (TEXT, NOT NULL)

- **device_types** (119 rows): Device type classifications
  - id (INTEGER, PK)
  - code (TEXT, NOT NULL)
  - description (TEXT)

- **devices** (14,669 rows): Main device catalog
  - id (INTEGER, PK)
  - manufacturer_id (INTEGER)
  - type_id (INTEGER)
  - model (TEXT)
  - name (TEXT)
  - symbol (TEXT)
  - properties_json (TEXT)

- **device_specs** (14,669 rows): Device electrical specifications
  - device_id (INTEGER, PK)
  - strobe_candela (REAL)
  - speaker_db_at10ft (REAL)
  - smoke_spacing_ft (REAL)
  - current_a (REAL)
  - voltage_v (REAL)
  - notes (TEXT)

- **wall_strobe_coverage** (6 rows): NFPA wall strobe coverage requirements
- **ceiling_strobe_coverage** (18 rows): NFPA ceiling strobe coverage requirements
- **strobe_candela** (7 rows): Strobe candela to radius mapping

### 🟢 ~/AutoFire/catalog.db - USER CATALOG DATABASE
**Location:** `C:\Users\{username}\AutoFire\catalog.db`
**Purpose:** User-specific device customizations and additions
**Size:** Small
**Tables:** Same structure as main DB, but only 14 demo devices

### 🟡 catalog.db - LEGACY DATABASE (SAFE TO DELETE)
**Location:** `c:\Dev\Autofire\catalog.db`
**Status:** NOT FOUND (already cleaned up)
**Purpose:** Old demo catalog, replaced by main database

## Database Architecture

### Connection Methods:
1. **Main App**: `db.connection.initialize_database()` → `autofire.db`
2. **Catalog Loading**: `app.catalog.load_catalog()` → uses main DB connection
3. **CLI Tools**: `autofire.cli.*` → uses main DB connection
4. **Legacy**: `db.loader.connect()` → `~/AutoFire/catalog.db` (deprecated)

### Data Flow:
- **Device Catalog**: Loaded from `autofire.db` via `app.catalog.load_catalog()`
- **NFPA Tables**: Coverage calculations from strobe tables
- **User Data**: Settings and preferences (future)

## Backup & Recovery

### Critical Files to Backup:
- `autofire.db` - Contains all device data
- `app/` directory - Application code
- `requirements.txt` - Dependencies

### Recovery Commands:
```bash
# Rebuild database from JSON files
python -c "from db import loader; loader.initialize_database()"

# Verify device count
python -c "from app import catalog; print(len(catalog.load_catalog()))"
```

## Development Notes

- **Row Factory**: Main DB uses `sqlite3.Row` for dict-like access
- **Foreign Keys**: manufacturer_id, type_id reference other tables
- **JSON Fields**: properties_json stores device-specific data
- **NFPA Data**: Pre-populated coverage tables for compliance calculations

---

**⚠️ WARNING: Never delete `autofire.db` - it contains the complete device catalog required for the application to function!**</content>
<parameter name="filePath">c:\Dev\Autofire\DATABASE_DOCUMENTATION.md
