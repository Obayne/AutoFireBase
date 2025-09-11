# CHANGELOG

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
