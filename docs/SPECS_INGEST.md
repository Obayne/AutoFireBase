Specs Ingest — Manufacturer Packs

Goal
- Normalize vendor PDFs (panels/devices/guides) into a JSON “manufacturer pack” usable by the app.

Folder
- vendor_specs/<vendor>/{panels,devices,guides}
- Output: vendor_specs/<vendor>/pack.json (generated)

Pack Schema (draft)
- vendor: string (e.g., "Fire-Lite")
- panels: [{ model, name, slots, outputs, loops, address_limit, standby_current_a, alarm_current_a, battery_sizing_method, notes }]
- devices: [{ model, name, type, addressable: bool, allowed_circuits: ["NAC"|"SLC"|"IDC"], standby_current_a, alarm_current_a, voltage_v, options: { candela: [...], db: [...] }, notes }]
- wiring_tables: { voltage_drop: [{ gauge_awg, max_len_ft_at_current, notes }], ampacity: [...] }
- docs: [{ path, kind: "panel"|"device"|"guide", model_hint, title }]

Notes
- PDFs remain in LFS; pack.json references them by relative path.
- Keep PRs small; HAL approves before merge.

