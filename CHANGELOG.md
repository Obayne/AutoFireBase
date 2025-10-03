# Changelog

## [0.7.0] - 2025-10-03 - **MAJOR ARCHITECTURAL RESTRUCTURE**
- **BREAKING**: Complete project restructure to modular architecture following AGENTS.md guidelines
- **REFACTOR**: Moved from monolithic `app/` structure to clean layered architecture:
  - `frontend/` - UI Layer (PySide6/Qt): windows, dialogs, controllers, views
  - `backend/` - Business Logic Layer: catalog, persistence, import/export services
  - `cad_core/` - CAD Algorithms Layer: tools, geometry, unit conversions
- **REMOVED**: Eliminated obsolete monolithic files (`app/main.py`, `app/main_fixed.py`, `app/main_startup_safety.py`, etc.)
- **ADDED**: `AutoFireController` class for multi-window application management
- **ADDED**: Qt signal system for cross-window communication (`model_space_changed`, `paperspace_changed`, `project_changed`)
- **FIXED**: `CanvasView` constructor corrected to match window instantiation requirements
- **ADDED**: Clean application entry point (`main.py` → `frontend/app.py`)
- **MOVED**: All UI components relocated to `frontend/` (windows, dialogs, assistants, coverage, wiring, settings)
- **MOVED**: CAD tools and algorithms moved to `cad_core/tools/`
- **MOVED**: Business logic moved to `backend/` (catalog, logging, DXF import, data services)
- **UPDATED**: All import statements updated to reflect new modular structure
- **MAINTAINED**: Full backward compatibility - application runs identically with same features
- **IMPROVED**: Clear separation of concerns enabling better testing, maintenance, and development
- **DOCUMENTED**: Comprehensive documentation added (`docs/ARCHITECTURE.md`, `docs/API_REFERENCE.md`, `docs/DEVELOPMENT_SETUP.md`, `docs/TROUBLESHOOTING.md`)
- **COMMIT**: `feat: Complete project restructure to modular architecture` (70 files changed, 715 insertions, 9034 deletions)

## [Unreleased] - 2025-09-26
- Added: Separate Windows Architecture - Model space and paperspace as independent windows for better multi-monitor support and cleaner workflow.
- Added: Project Overview Window - Central hub for project management with organizer sections (notes, milestones, progress), calendar for scheduling, and AI assistance for manipulation.
- Added: AI Assistant docks integrated throughout the application (Model Space, Paperspace, Project Overview) for natural language queries to manipulate plans/drawings.
- Updated: GUI main structure refactored to use AppController for multi-window management; main.py delegates to controller.
- Added: Centralized structured logging via `app/logging_config.py`; entrypoints now use structured loggers.
- Added: Headless palette → placement simulation harness (`run_logs/run_all_simulations.py`) to validate placement flows without the GUI.
- Added: Canonical stash/pop conflict resolver with safe wrapper scripts (`scripts/tools/_auto_resolve_conflicts.py` and delegates). Automatic edits create `.bak-*` backups to preserve originals.
- Added: Comprehensive DXF import tests (`tests/test_dxf_import.py`) validating color mapping, unit conversion, and file import functionality.
- Added: Draw tools tests (`tests/test_draw_tools.py`) validating controller logic, geometry calculations, and mode handling for all draw operations (line, rect, circle, polyline, arc, wire).
- Added: Modify tools tests (`tests/test_trim_tool.py`, `tests/test_move_tool.py`) validating trim and move operations with intersection calculations and item manipulation.
- Validated: OSNAP (Object Snap) features are implemented with menu toggles for endpoint, midpoint, center, intersection, and perpendicular snaps; functionality confirmed through menu integration and core geometry logic.
- Planned: **Summary Window** - Third window for project management with progress tracking, notes, milestones, AI assistance, and live project analytics (multiview settings integration).
- Planned: **Separate Windows Architecture** - Model space and paperspace as independent windows instead of scene switching for cleaner workflow and better multi-monitor support.
- Fix: Multiple small conservative fixes to unblock imports and linting (renamed ambiguous single-letter variables in tests and tools; removed unused local assignments; fixed a nested triple-quote parse error in an archive hotfix file so Black can run).
- Fix: Corrected `simulate_palette_selection.py` to properly use local fallback device tree when Qt widgets are not available in headless mode.
- Note: `scripts/archive/` contains local-only snapshot scripts that were temporarily restored during a GUI rollback; these files should be treated as local-only and excluded from repo-wide lint/format passes (we will document and configure that exclusion).

## [0.4.7] - 2025-09-12
- Fillet radius UI + CAD core geometry (lines, circles, fillets)

## 0.4.6 - 2025-09-12
- Add CAD core line geometry scaffold and tests
- Add repo hygiene, CI, and release workflow

- Added: DXF underlay import with layer-aware rendering and auto-fit.
- Added: Draw tools (Line, Rect, Circle, Polyline, Arc-3pt), Wire, Text.
- Added: Modify tools (Offset Selected…, Trim Lines, Extend Lines, Fillet/Corner, Fillet/Radius, Rotate, Mirror, Scale, Chamfer).
- Added: Measure tool (temporary readout).
- Added: OSNAP (Endpoint/Midpoint/Center/Intersection/Perpendicular) with toggles under View.
- Added: Export PNG/PDF (letter landscape, fit to content).
- Added: Settings menu with themes (Dark/Light/High Contrast) and improved menu contrast.
- Improved: Panning (Space or Middle Mouse), Esc commits polyline, sketch/wires included in Save/Open.
- UI: Keep Draw/Modify in menus; removed CAD toolbars from top bar; status bar shows Grid opacity and Grid size.
- Added: DXF Layers dock (visibility, color override, lock, print flags).
- Added: Command Bar (commands + coordinate entry in feet; absolute, relative, polar).
- Coverage: Placement and global/per-device overlay toggles; Candela mapping for strobes (placeholder).
- DB: SQLite catalog scaffold (auto-created at %USERPROFILE%/AutoFire/catalog.db); palette loads from DB if present and seeds demo devices.
- Annotations: MText (scalable) and Freehand sketch tool added.
- UI: Device Palette is now a dockable panel (tabbed with other docks); Properties and DXF Layers appear as tabs.
- Underlay: Added scale by reference (two picks + real distance), scale by factor, and scale by drag (anchor + live factor); respect non-print DXF layers on export; underlay transform persists with project.

## 0.5.3 – coverage + array (2025-09-08 21:04)
- Restored **Coverage** overlays:
  - Detector circle
  - Strobe ceiling (circle + square)
  - Strobe wall (rectangle)
  - Speaker (circle)
- Coverage dialog supports **feet/inches**; app computes `computed_radius_px` from your current scale.
- Restored **Place Array…** tool: rows/cols with **ft/in spacing** copied from an anchor device.
- Context menu **Toggle Coverage** defaults to a 25 ft detector circle.
- Keeps earlier fixes: Qt `QShortcut` import, robust `boot.py` startup.


## v0.6.2 – overlayA (stability + coverage, 2025-09-11)
- **Grid**: always-on draw; major/minor lines; origin cross; tuned contrast for dark theme.
- **Selection**: high-contrast selection halo for devices.
- **Coverage overlays**:
  - Per-device **Coverage…** dialog with **Strobe / Speaker(dB) / Smoke** modes.
  - Strobe: manual **coverage diameter (ft)**; ceiling mount shows **circle in square** footprint.
  - Speaker: **inverse-square** model (L@10ft → target dB) to compute radius.
  - Smoke: simple **spacing (ft)** ring (visual guide).
  - Toggle coverage on/off via right-click.
- **Live preview**: when a palette device is active, a **ghost device + coverage** follows your cursor (editable after placement).
- **Array**: “Place Array…” uses **coverage-driven spacing** by default (with manual override).
- **Persistence**: overlays and settings persist via `.autofire` save files and user preferences.
- **Notes**: NFPA/manufacturer tables will be wired next; current coverage helpers are conservative visual aids.


## v0.6.3 – overlayB (2025-09-11)
- **Overlays** now show **only** for strobe / speaker / smoke device types (no coverage on pull stations).
- **Quick coverage adjust**:
  - **[ / ]** → strobe coverage **diameter −/+ 5 ft**
  - **Alt+[ / Alt+]** → speaker **target dB −/+ 1 dB**
- **Grid** is lighter by default; added **View → Grid Style…** for opacity, line width, and major-line interval (saved in prefs).
- Persisted grid style in project saves; status bar messages clarify current adjustments.
