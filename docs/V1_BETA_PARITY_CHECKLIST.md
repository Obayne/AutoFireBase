# V1 Beta Competitive Parity Checklist (FireCAD)

Scope: Minimum set to be competitive in core workflows while staying true to AutoFire’s CAD-first approach.

Legend: [ ] todo, [~] partial, [x] done


## 1) Project setup and backgrounds

- [x] Model Space underlay + two-point scale calibration persisted (px_per_ft)
- [ ] Import PDF to raster background (pdf→image) with DPI hint; reuse scale flow
- [ ] New Project wizard (folder, project name, select background file) and link in left “Project” dock
- [ ] Title/metadata panel (project, AHJ notes, NFPA 72 checklist generator in reports)

Acceptance:

- Designer can create a project folder, import a PDF/image as underlay, and calibrate scale once; scale persists across sessions.


## 2) Device palette and placement

- [~] Device palette dock with search filter and category tree
- [ ] Click-to-place devices with smart snapping; post-place panel/circuit quick-assign dialog (skippable)
- [ ] Bulk replace part on selection without disconnecting (safe migration)

Acceptance:

- Designer can search and place devices rapidly; optional panel/circuit assignment dialog appears and can be cancelled.


## 3) Project Circuits Editor (MVP)

- [ ] Dockable grid with filter row
- [ ] Columns: Panel, Node/Card, Circuit, Type, Cable, EOL, T‑Tap, Hidden, Locked, Start Addr
- [ ] Editable: Circuit, Cable, EOL, T‑Tap, Hidden, Locked, Start Addr (with validation)
- [ ] Actions: Update Wire Labels, Recompute Calcs (stubs initially)
- [ ] Hide/Lock affects connection pickers and edits

Acceptance:

- Grid updates reflect in model (labels, visibility) and vice versa; filter makes large projects manageable.


## 4) Wirepaths, labels, and conduit fill

- [ ] Wirepath entity model with attributes: cable, conduit type/size, fill %, label mode
- [ ] Conduit fill calculation in cad_core; support EMT/PVC/RGS tables and AWG/cable mappings
- [ ] Label overlays that show cable abbreviations; toggle “Hide Conduit Fill”
- [ ] Option to encode cable abbreviations into linetype (phase 2)

Acceptance:

- Selecting wirepaths and setting conduit type/size produces correct fill % labels; toggle works globally/per-wirepath.


## 5) NAC ↔ FACP connections and riser export

- [ ] Connection types: ReversePolarity, VendorBus(P‑Link/RUI/V‑Link), RemoteSync, RelayContact + MonitorZone
- [ ] Compatibility rules for which devices/circuits can connect
- [ ] Riser data export (JSON/CSV) summarizing panels, circuits, and connections; simple diagram later

Acceptance:

- Designer can connect a NAC panel using Method 1 or Method 4; export shows connections in a riser-friendly list.


## 6) Parts/catalog sourcing

- [~] Local catalog (SQLite/JSON) with manufacturers/parts
- [ ] “Connect Catalog” dialog: choose local file, pick manufacturer presets (templates)
- [ ] CSV importer to seed/update catalog; audit log of changes

Acceptance:

- New project can pick a local catalog and a manufacturer preset to filter the device palette and default calcs.


## 7) Reports and data export

- [ ] Export All Project Data (XLSX/CSV) with devices, circuits, wirepaths, panels, and calc fields
- [ ] NFPA 72 checklist stub report populated from project metadata

Acceptance:

- One‑click export produces a structured file usable by downstream processes; NFPA checklist appears with project metadata.


## Cross‑cutting quality

- [x] No‑splash startup and headless import (CI‑friendly)
- [ ] Layout persistence for docks and editors across sessions
- [ ] Pre‑commit green (ruff/black), unit tests for calc kernels


## Module mapping

- frontend/
  - project_palette.py (wizard + linking)
  - device_palette.py (search + place)
  - circuits_editor.py (grid)
  - labels_manager.py (wirepath labels)

- cad_core/
  - conduit_fill.py (tables + math)
  - cable_catalog.py, conduit_catalog.py
  - connections.py (compatibility, validation)

- backend/
  - catalog_store.py (SQLite/JSON, CSV import)
  - riser_export.py (data export)
  - project_store.py (prefs, metadata)


## Notes

- We prioritize parity where it improves designer throughput (circuits editor, fill, connections). Paper‑space and .dwg templates are out of scope; our reports and exports carry that value instead.
