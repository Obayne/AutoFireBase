# AutoFire Project Changelog

## [Unreleased]

### Fixed
- Resolved application startup issues:
  - Corrected `boot.py` path in `Run_AutoFire_Debug.ps1`.
  - Recreated virtual environment and reinstalled dependencies.
  - Fixed syntax error in `app/main.py` (misplaced `TokenItem` import).
  - Corrected `MainWindow` initialization order by ensuring `self.tab_widget` is defined before `_init_sheet_manager` is called.
- Updated database schema in `db/schema.py` to include `circuits` and `wire_specs` tables, and new columns (`circuit_id`, `standby_current_ma`, `alarm_current_ma`) in `devices` and `device_specs` tables.
- Fixed the broken crosshairs by ensuring they are always visible and span the entire viewport when enabled.
- Fully restored and corrected the `DeviceItem` class to fix device placement and related crashes.
- Refactored the device filter dropdowns to correctly populate with unique values.
- Adjusted spacing in the left panel to reduce crowding.
- Fixed a `NameError` crash in the `DeviceItem` class by adding a missing import.
- Refactored the device search logic to fix inconsistent and incorrect results.
- Fixed a bug in the FACP Wizard that prevented panels from being placed.
- Restored the `DeviceItem` class to its correct state to fix multiple crashes and regressions.
- Optimized the right-click context menu to prevent mouse pointer lag and warping.
- Fixed a critical bug where device placement was broken due to an error in the `DeviceItem` class.
- Removed the automatic creation of old paperspace items on the canvas.
- Removed hardcoded stylesheets from the left panel to allow themes to apply correctly.

### Added
- Full implementation of the Layer Management system:
  - Enabled editing of layer properties (name, color, visible, locked, show name, show part number) directly in the table.
  - Implemented color picker for layers.
  - Ensured changes to layer properties are reflected on the canvas.
  - Implemented 'Active' layer functionality: a radio button in the layer table allows designating one layer as active, and new devices are assigned to this active layer.
- Initial implementation of the Token System:
  - Added `TokenSelectorDialog` to select tokens.
  - Added 'Place Token' action to the 'Tools' menu, allowing placement of simple text tokens on the canvas.
  - Implemented logic to link placed tokens to device data:
    - Created `TokenItem` class to represent data-bound tokens.
    - Modified `place_token` to place `TokenItem` instances linked to selected devices.
    - Updated serialization/deserialization to save and load `TokenItem`s.
  - Enhanced Layer Manager to provide granular control over token visibility:
    - Added new columns to the `layers` table for token visibility options.
    - Updated `LayerManagerDialog` to display checkboxes for these options.
    - Modified `TokenItem` to check its layer's properties to determine its visibility.
- Enhanced Connections Tree:
  - Modified `add_panel` and `add_device_to_panel` methods to store references to `DeviceItem` objects.
  - Updated `get_connections` and `load_connections` methods to handle these references.
  - Added context menus to the `ConnectionsTree` with actions like 'Go to Device', 'Select Device', and 'View Properties'.
  - Implemented removal of devices from the `ConnectionsTree` when they are deleted from the canvas.
- Initial database schema changes for circuits:
  - Added a new `circuits` table.
  - Added a `circuit_id` column to the `devices` table.
- Implemented smart wiring tools that understand circuit types (SLC, NAC) and device compatibility:
  - Added `circuit_type` to `WireTool`.
  - Implemented `_check_compatibility` method in `WireTool`.
  - Updated `DeviceItem` to include `slc_compatible` and `nac_compatible` attributes.
  - Modified `fetch_devices` to retrieve compatibility attributes from the database.
- Initial UI for managing circuit properties:
  - Added a 'Circuit Type' column to the `ConnectionsTree`.
  - Modified `add_panel` to set the circuit type for the panel item.
  - Integrated the `CircuitPropertiesDialog` into the `ConnectionsTree` context menu.
- Added functionality to manage circuit properties:
  - Added `save_circuit` and `fetch_circuit` functions to `db/loader.py`.
  - Modified the `CircuitPropertiesDialog` to save changes to the database.
  - Modified `ConnectionsTree` to load circuit data.
- Initial implementation of calculation engine:
  - Created `app/calculations.py` module with voltage drop and battery size calculation functions.
- Initial UI integration for calculations:
  - Created `CalculationsDialog`.
  - Added 'Show Calculations' action to the 'Tools' menu.
- Implemented real-time voltage drop and battery size calculations:
  - Implemented the calculation logic within the `CalculationsDialog` to fetch data, perform calculations, and display results.
- Initial implementation of Bill of Materials (BOM) report:
  - Created `BomReportDialog`.
  - Added 'Bill of Materials (BOM)' action to the 'File' -> 'Export' menu.
- Initial implementation of Device Schedule report:
  - Created `DeviceScheduleReportDialog`.
  - Added 'Device Schedule' action to the 'File' -> 'Export' menu.
- Initial implementation of Riser Diagram generation tool:
  - Created `RiserDiagramDialog`.
  - Added 'Generate Riser Diagram' action to the 'Tools' menu.
- Full implementation of Paperspace mode:
  - Created a separate Paperspace scene.
  - Implemented `ViewportItem` to display Modelspace within Paperspace.
  - Integrated a `QTabWidget` for managing multiple Paperspace layouts (sheets).
- Initial implementation of Riser Diagram generation tool:
  - Created `RiserDiagramDialog`.
  - Added 'Generate Riser Diagram' action to the 'Tools' menu.
- Initial implementation of Bill of Materials (BOM) report:
  - Created `BomReportDialog`.
  - Added 'Bill of Materials (BOM)' action to the 'File' -> 'Export' menu.
- Database schema enhancements for calculations:
  - Added `standby_current_ma` and `alarm_current_ma` to `fire_alarm_device_specs`.
  - Added a `wire_specs` table.
  - Added `panel_standby_current_ma` and `panel_alarm_current_ma` to the `devices` table.
  - Updated `seed_demo` function to populate these new fields.

### Changed
- Reorganized the left device palette for a more intuitive workflow:
  - Created a new "System" group box at the top.
  - Moved the "System Configuration Wizard" button into the "System" group.
  - Added a new "Wire Spool" button to the "System" group as a placeholder for future functionality.
  - Made the "System" and "Device Palette" sections collapsible.
  - Moved the device search bar into the "Device Palette" section.

### Added
- Created this CHANGELOG.md file to track project modifications.
- Implemented a "Wire Spool" dialog that loads wire types from the database.
- Added a "Connections Tree" window to display the system's wiring hierarchy.
- Implemented a "Draw Wire" tool for drawing connections between devices.
- Implemented saving and loading of connection data with the project.
- Added a Settings dialog with options to change the theme and primary color.
- Added a dedicated CAD toolbar with 'Measure' and 'Scale' tools for better accessibility.
- Implemented a new Layer Management system:
  - Added a `layers` table to the database and associated devices with layers.
  - Created a `LayerManagerDialog` to create, rename, and delete layers.
  - Device visibility, color, and attribute visibility are now controlled by layer properties.

### Backup
- Created a complete backup of the project in `C:\Dev\Autofire_backup_2025_09_21` on 2025-09-21.
