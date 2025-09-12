# Changelog


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


