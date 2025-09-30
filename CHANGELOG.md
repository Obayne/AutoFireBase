# Changelog

All notable changes to AutoFire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-09-29

### Added

- Added repository recovery and backup procedures (RECOVERY.md) and a lightweight backup script (`scripts/backup_repo.ps1`). These files provide a safe, simple way to snapshot the repo before large refactors.


### Fixed

### Improved

### Paperspace (Unreleased)

## Unreleased

- Paperspace: add rich-text, collapsible Notes group
  - Notes editor moved into a checkable QGroupBox in the Paperspace Properties UI.
  - Notes now support basic rich-text (HTML) and are preserved when applying, exporting, and saving system configuration.
  - Added unit tests to verify notes group behavior and HTML round-trip.
- Task: Add Paperspace tabs & UI polish (in-progress)
- Task: Validation & sync fields (in-progress)
- **Overlays** now show **only** for strobe / speaker / smoke device types (no coverage on pull stations).
- **Quick coverage adjust**:
- **Grid** is lighter by default; added **View  Grid Style** for opacity, line width, and major-line interval (saved in prefs).
- Persisted grid style in project saves; status bar messages clarify current adjustments.
- **Grid**: always-on draw; major/minor lines; origin cross; tuned contrast for dark theme.
- **Selection**: high-contrast selection halo for devices.
  - Speaker: **inverse-square** model (L@10ft  target dB) to compute radius.
  - Smoke: simple **spacing (ft)** ring (visual guide).
  - Toggle coverage on/off via right-click.
- **Live preview**: when a palette device is active, a **ghost device + coverage** follows your cursor (editable after placement).
- **Array**: "Place Array" uses **coverage-driven spacing** by default (with manual override).
- Restored **Coverage** overlays:
  - Detector circle
  - Strobe wall (rectangle)
  - Speaker (circle)
- Coverage dialog supports **feet/inches**; app computes computed_radius_px from your current scale.
- Restored **Place Array** tool: rows/cols with **ft/in spacing** copied from an anchor device.
- Fillet radius UI + CAD core geometry (lines, circles, fillets)

- Add CAD core line geometry scaffold and tests
- Add repo hygiene, CI, and release workflow
- Added: DXF underlay import with layer-aware rendering and auto-fit.
- Added: Draw tools (Line, Rect, Circle, Polyline, Arc-3pt), Wire, Text.
- **Grid**: always-on draw; major/minor lines; origin cross; tuned contrast for dark theme.
