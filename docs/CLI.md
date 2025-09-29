AutoFire CLI Quick Reference

Installation
- From repo root (dev): `pip install -e .`
- Entry point: `autofire-cli`

Device Commands
- `autofire-cli device list [--type TYPE] [--manufacturer MFG]`
- `autofire-cli device search QUERY`
- `autofire-cli device add --name NAME --type TYPE [--manufacturer MFG] [--part-number PN]`
- `autofire-cli device export [--format json|csv] [--output FILE]`
- `autofire-cli device import INPUT [--format json|csv]`
- `autofire-cli device stats`
- `autofire-cli device report bom --format csv|json [--output FILE]`
- `autofire-cli device report device-schedule --format csv|json [--output FILE]`
- `autofire-cli device types` — list device types
- `autofire-cli device manufacturers` — list manufacturers
- `autofire-cli device show (--id ID | --name NAME | --part-number PN | --contains TEXT) [--all]`
- `autofire-cli device count --by type|manufacturer [--json] [--output FILE]`

Database Admin
- `autofire-cli device db-init`
- `autofire-cli device db-seed`
- `autofire-cli device db-backup backup.db`
- `autofire-cli device db-restore backup.db`

Tips
- Set `AUTOFIRE_DB_PATH` to use a custom SQLite location (see `docs/DATABASE.md`).
