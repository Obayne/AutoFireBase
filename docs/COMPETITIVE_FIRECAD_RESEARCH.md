# Competitive Research — FireCAD/ Cadgen

Sources reviewed (Oct 26, 2025):
- Creating a project drawing using the FireCAD provided basic templates
  https://support.cadgen.com/hc/en-us/articles/4404328389140-Creating-a-project-drawing-using-the-FireCAD-provided-basic-templates
- Create a Project, Import PDF Background (Example 1)
  https://support.cadgen.com/hc/en-us/articles/360035833351-Create-a-Project-Import-PDF-Background-Example-1
- Using The Project Circuits Editor
  https://support.cadgen.com/hc/en-us/articles/8713047388052-Using-The-Project-Circuits-Editor
- Showing/Hiding Conduit Fill
  https://support.cadgen.com/hc/en-us/articles/4407183318548-Showing-Hiding-Conduit-Fill
- How to connect to the Cadgen parts database
  https://support.cadgen.com/hc/en-us/articles/360062451791-How-to-connect-to-the-Cadgen-parts-database
- How to connect to a local database (.MDF) file
  https://support.cadgen.com/hc/en-us/articles/4401749630612-How-to-connect-to-a-local-database-MDF-file
- Connecting NAC Panels to Fire Alarm Control Panels (overview of methods)
  https://support.cadgen.com/hc/en-us/articles/11433503350164-Connecting-NAC-Panels-to-Fire-Alarm-Control-Panels (content also appears embedded in circuits editor context)


## Core workflows and features (FireCAD)

- Project templates and paper space layout
  - Provides downloadable .dwg templates (ARCH D/E/E1), with model space guidance (yellow non-plot layer) and paper space tabs aligned to model-space rectangles.
  - Title block workflows, NFPA 72 checklist on-sheet, and guidance on relationship of model space to layout sheets.

- PDF/vector background import and scale calibration
  - Import vector PDF as background (Insert → PDF Import) and scale to real-world units by measuring door width (36") and using reference scaling.
  - Emphasis: correct scale is prerequisite for accurate reports.

- Project creation, database, and drawing linking
  - Wizard to create project DB, choose master parts connection (cloud SQL Server or local .MDF), and copy selected manufacturer templates into local project DB.
  - Link project DB to one or more background drawings; save and manage via a left dock “Project Palette/Tree”.

- Device placement and search
  - Device palette with filter-by-text; click-to-place block on model space. Post-place dialogs for panel/module assignment or circuit settings (can be cancelled for quick layout).

- Project Circuits Editor (grid UI)
  - Global grid listing circuits with filters; supports rename, lock/unlock, hide/unhide from selection lists.
  - Supports EOL notation per circuit; cable override per circuit; influences wirepath labels and calculations (battery, voltage drop).
  - Wirepath labeling as multileaders or encoded linetypes; update labels command to reflect changes.
  - T-tapping: per-circuit setting affects wirefill and downstream calcs.
  - Advanced controls: report order, connectivity behavior, starting address overrides, thresholds.

- Conduit fill calculation and visibility
  - Assign conduit type/size to wirepaths; compute fill %; render as a label (toggle visibility). Option to encode cable abbreviations in linetype and show fill as label.

- NAC panel connections to FACP (methods)
  - Method 1: FACP NAC to NAC panel reverse-polarity DC input; show connection on floor plan and riser; appears in connected device list.
  - Method 2: Proprietary buses (e.g., Potter P-Link, Simplex/Autocall RUI, ADEMCO V-Link): connect via vendor protocol circuit.
  - Method 3: Remote sync terminals (strobe sync) as activation signal.
  - Method 4: General relay contact activation + monitor modules for trouble/AC failure; show SLC connections and device lists; riser confirms.


## Data model implications

- Project as a container with:
  - Background drawings (1..n), scale (px/ft), coordinate system.
  - Panels (FACP, NAC panels, expanders), circuits (typed: NAC, SLC, vendor buses, relay, monitor zone), devices (detectors, modules, horns, strobes).
  - Wirepaths as polylines with attributes: cables, conduit type/size, computed fill %, labeling mode.
  - Circuit-to-device and circuit-to-panel connections with compatibility constraints.
  - Calculation inputs/overrides: cable type per circuit, EOL notes, t-tap flags, thresholds, starting addresses.


## UX patterns to note

- Left dock “Project Palette/Tree” + “Device Palette” with search.
- Central model space always visible; PDF/vector background underlay; quick reference-based scaling.
- Circuits Editor as a dockable grid with filter row and editable cells with guardrails.
- Commands for “Update All Wire Labels”, “Set Conduit Type”, “Hide Conduit Fill”, “Format Wirepath Labels”.


## AutoFire v1 beta — current vs. gaps

- Already in-progress/available
  - CAD-first model space with floorplan underlay and two-point calibration → px_per_ft persisted to prefs.
  - Window Manager, dock system, and Project Circuits Editor dock placeholder present.
  - Unified app entry with no-splash/headless modes for fast startup and CI.

- Partial/needs build-out
  - Project Circuits Editor grid behaviors: filter row, per-circuit rename/lock/hide, cable override, EOL notation, t-tap flag, starting address override; recompute labels and calcs.
  - Device palette with search-first placement; lightweight post-place assignment (panel/module/circuit) UX.
  - Wirepath labeling pipeline: label overlays vs encoded linetype; “Update All Wire Labels” command.

- Not yet implemented (parity targets)
  - Conduit fill math + label toggle; conduit type/size assignment on wirepaths.
  - NAC↔FACP connection modes (reverse-polarity, proprietary buses, remote sync, relay/monitor) + riser export reflecting those connections.
  - External parts DB connectors workflow: we’ll target SQLite/local catalogs and CSV import first (not SQL Server .MDF). Manufacturer “templates” as presets of part families.
  - Project creation wizard with local DB seed selection and drawing linking UI.


## Quick-win recommendations (next sprint)

1) Circuits Editor MVP
- Grid with filter row; columns: Panel, Node/Card, Circuit Name, Type, Cable, EOL, T-Tap, Hidden, Locked.
- Editable: Name, Cable, EOL, T-Tap, Hidden, Locked.
- Actions: Update Wire Labels, Recompute Calcs (battery/voltage drop stubs initially).

2) Wirepath + labels foundation
- cad_core: cable catalog, conduit catalog, fill computation; per-wirepath attributes.
- frontend: label overlay manager; toggle “Hide Conduit Fill”; label layout rules.

3) NAC/FACP connection primitives
- backend: connection model enums (ReversePolarity, VendorBus(P-Link/RUI/V-Link), RemoteSync, RelayContact + MonitorZone).
- Exporter: riser data stub listing connections by method; simple diagram generator later.

4) Parts/catalog strategy
- Unify around our SQLite/JSON catalogs; importer from CSV; “templates” = named presets.
- UI: small “Connect Catalog” dialog to pick source (local file) + active manufacturer preset.


## Risks and notes

- We’re not an AutoCAD OEM; paper space-style layout tabs and .dwg templates don’t directly apply. Our focus: model space CAD and first-class reports.
- PDF import for vector content may require conversion; near-term, support raster underlay (pdf→image) plus scale calibration.
- Calculation parity (battery, voltage drop) requires vetted formulas per manufacturer; we’ll expose hooks and start with conservative generic calcs.


## Acceptance signals

- Designer can: import floorplan underlay → calibrate scale → place devices via search → connect circuits → edit circuits in grid → set cable/labels → toggle conduit fill → export riser data listing connections.
- No-splash startup < 3s on dev machines; headless import works in CI.
