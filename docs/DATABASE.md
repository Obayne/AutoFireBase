AutoFire Database Guide

Overview
- SQLite is used for catalog and coverage data.
- Default DB path: `~\AutoFire\catalog.db` (see `db/loader.py:DB_DEFAULT`).
- Schema is created and demo data is seeded automatically by helpers.

Core Tables
- `manufacturers(id, name)` — unique manufacturer names.
- `device_types(id, code, description)` — unique type codes (e.g., Detector).
- `devices(id, manufacturer_id, type_id, model, name, symbol, properties_json)` — device catalog.
- `device_specs(device_id, strobe_candela, speaker_db_at10ft, smoke_spacing_ft, current_a, voltage_v, notes)` — optional specs.

Coverage Tables (`db/coverage_tables.py`)
- `wall_strobe_coverage(room_size INTEGER PRIMARY KEY, candela INTEGER)`
- `ceiling_strobe_coverage(ceiling_height INTEGER, room_size INTEGER, candela INTEGER, PRIMARY KEY (ceiling_height, room_size))`
- `strobe_candela(candela INTEGER PRIMARY KEY, radius_ft REAL)`

CLI Tasks (scripts/device_cli.py)
- List/search devices
- Show device details
- Count devices
- Export/import catalog
- Stats summary
- Database admin

Examples
- List/search
  - `python scripts\device_cli.py list [--type TYPE] [--manufacturer MFG]`
  - `python scripts\device_cli.py search QUERY`
- Show details
  - Exact: `python scripts\device_cli.py show --id ID | --name NAME | --part-number MODEL`
  - Partial: `python scripts\device_cli.py show --contains TEXT [--all]`
- Count
  - `python scripts\device_cli.py count --by type|manufacturer [--json] [--output FILE]`
- Export/import
  - Export: `python scripts\device_cli.py export --format json|csv [--output FILE]`
  - Import: `python scripts\device_cli.py import INPUT --format json|csv`
- Stats
  - `python scripts\device_cli.py stats`
- DB admin
  - Init schema: `python scripts\device_cli.py db-init`
  - Seed demo: `python scripts\device_cli.py db-seed`
  - Backup: `python scripts\device_cli.py db-backup backup.db`
  - Restore: `python scripts\device_cli.py db-restore backup.db`

Notes
- Exports use UTF-8 when writing files; JSON printed to console uses ASCII-safe escapes for Windows shells.
- The CLI seeds demo data if the database is empty to ensure commands work out of the box.
- Programmatic access is available via `db/loader.py` (connect, ensure_schema, seed_demo, fetch/search APIs).

Environment Override
- Set `AUTOFIRE_DB_PATH` to point CLI and code to a custom SQLite path.
  - PowerShell: `$env:AUTOFIRE_DB_PATH = "C:\\temp\\af_catalog.db"`
  - Bash: `export AUTOFIRE_DB_PATH=/tmp/af_catalog.db`
  - Code: `db_loader.connect()` will pick it up automatically.

Migration Strategy (Guidance)
- Prefer additive, backward-compatible schema changes.
- Use `ensure_schema(con)` for idempotent table creation; for changes, use `ALTER TABLE` guarded by existence checks.
- Back up first: `device_cli.py db-backup` and restore if needed.
- If a breaking change is unavoidable, add a one-time migration in `db/loader.py` gated by a feature flag or schema marker.
