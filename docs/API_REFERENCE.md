# API Reference

This document provides detailed API documentation for the key classes and interfaces in AutoFire.

## Frontend Layer

### AutoFireController

**Location**: `frontend/controller.py`

The main application controller that manages the multi-window application lifecycle.

#### Signals
- `model_space_changed(dict)`: Emitted when model space content changes
- `paperspace_changed(dict)`: Emitted when paperspace content changes
- `project_changed(dict)`: Emitted when project state changes

#### Methods
```python
def __init__(self) -> None
```
Initializes the controller, loads preferences and device catalog, creates windows.

```python
def create_global_menu_bar(self, window: QMainWindow) -> None
```
Creates a standardized menu bar for application windows.

```python
def save_preferences(self) -> None
```
Persists user preferences to disk.

---

### ModelSpaceWindow

**Location**: `frontend/windows/model_space.py`

Primary CAD workspace for device placement and design.

#### Constructor
```python
def __init__(self, app_controller: AutoFireController, parent=None) -> None
```

#### Key Methods
```python
def _setup_scene_and_view(self) -> None
```
Initializes the CAD scene and graphics view.

```python
def _setup_ui(self) -> None
```
Creates docks, toolbars, and UI components.

```python
def on_model_space_changed(self, change_data: dict) -> None
```
Handles model space updates from other windows.

---

### PaperspaceWindow

**Location**: `frontend/windows/paperspace.py`

Print layout and documentation workspace.

#### Constructor
```python
def __init__(self, app_controller: AutoFireController, model_scene: GridScene, parent=None) -> None
```

#### Key Methods
```python
def _setup_paperspace_scene(self) -> None
```
Initializes the paperspace layout scene.

```python
def on_paperspace_changed(self, change_data: dict) -> None
```
Handles paperspace-specific updates.

---

### ProjectOverviewWindow

**Location**: `frontend/windows/project_overview.py`

Project management hub with notes, calendar, and AI assistance.

#### Constructor
```python
def __init__(self, app_controller: AutoFireController, parent=None) -> None
```

#### Key Methods
```python
def _setup_tabs(self) -> None
```
Creates overview, calendar, and AI assistant tabs.

---

## Backend Layer

### Catalog Management

**Location**: `backend/catalog.py`

#### Functions
```python
def load_catalog() -> list[dict]
```
Loads the complete device catalog from database.

Returns a list of device dictionaries with standardized fields:
- `name`: Display name
- `symbol`: Short symbol/abbreviation
- `type`: Device type (Detector, Notification, etc.)
- `manufacturer`: Manufacturer name
- `part_number`: Part number
- `specs`: Technical specifications

---

### Data Services

**Location**: `backend/data/`

#### SQLiteStore

**Location**: `backend/data/sqlite_store.py`

Database persistence layer for projects and configurations.

```python
def save_project(project_data: dict) -> int
```
Saves project data and returns project ID.

```python
def load_project(project_id: int) -> dict | None
```
Loads project data by ID.

---

### Import/Export Services

**Location**: `backend/dxf_import.py`

#### Functions
```python
def import_dxf(file_path: str) -> dict
```
Imports DXF file and returns structured data.

```python
def export_dxf(scene_data: dict, file_path: str) -> bool
```
Exports scene data to DXF format.

---

## CAD Core Layer

### Tools Framework

**Location**: `cad_core/tools/`

All CAD tools follow a consistent interface:

```python
class CadTool:
    def start(self, **kwargs) -> None:
        """Begin tool operation"""
        pass

    def update(self, **kwargs) -> None:
        """Update tool state during operation"""
        pass

    def cancel(self) -> None:
        """Cancel current operation"""
        pass

    def commit(self) -> None:
        """Complete and apply operation"""
        pass
```

#### Available Tools

- **Draw Tools**: Line, circle, rectangle, polygon drawing
- **Modify Tools**: Move, rotate, scale, mirror operations
- **Measure Tools**: Distance, area, angle measurements
- **Utility Tools**: Trim, extend, fillet, chamfer

---

### Geometry Operations

**Location**: `cad_core/tools/draw.py`

#### Key Functions
```python
def _circle_from_3pts(a: QPointF, b: QPointF, c: QPointF) -> tuple[QPointF, float, tuple[float, float]]
```
Calculates circle parameters from three points.

Returns: (center, radius, (start_angle, span_angle))

---

### Unit Conversions

**Location**: `cad_core/units.py`

#### Functions
```python
def ft_to_px(ft: float, px_per_ft: float = 12.0) -> float
```
Converts feet to pixels.

```python
def px_to_ft(px: float, px_per_ft: float = 12.0) -> float
```
Converts pixels to feet.

```python
def fmt_ft_inches(ft: float) -> str
```
Formats feet as feet-inches string (e.g., "12'6\"").

---

## Database Layer

### Database Loader

**Location**: `db/loader.py`

#### Functions
```python
def connect() -> sqlite3.Connection
```
Creates database connection with proper configuration.

```python
def ensure_schema(conn: sqlite3.Connection) -> None
```
Creates tables and indexes if they don't exist.

```python
def seed_demo(conn: sqlite3.Connection) -> None
```
Populates database with demo data.

```python
def fetch_devices(conn: sqlite3.Connection) -> list[dict]
```
Retrieves all devices from database.

---

## Configuration

### Preferences Structure

User preferences are stored as JSON in `~/AutoFire/preferences.json`:

```json
{
  "px_per_ft": 12.0,
  "grid": 12,
  "snap": true,
  "show_coverage": true,
  "page_size": "Letter",
  "page_orient": "Landscape",
  "page_margin_in": 0.5,
  "grid_opacity": 0.25,
  "grid_width_px": 0.0,
  "grid_major_every": 5,
  "print_in_per_ft": 0.125,
  "print_dpi": 300,
  "theme": "dark",
  "units": "Imperial (feet)",
  "drawing_scale": "1:1",
  "default_line_weight": 1,
  "default_color": "#000000",
  "show_device_palette": true,
  "show_properties_dock": true,
  "show_status_bar": true,
  "auto_save_interval": 5,
  "enable_osnap": true,
  "show_grid": true
}
```

### Logging Configuration

**Location**: `backend/logging_config.py`

```python
def setup_logging(level: str = "INFO") -> None
```
Configures application-wide logging to `~/AutoFire/logs/`.

---

## Error Handling

### Exception Types

- `ValueError`: Invalid input parameters
- `FileNotFoundError`: Missing files or resources
- `sqlite3.Error`: Database operation failures
- `ImportError`: Missing dependencies

### Error Recovery

- Database errors: Fall back to built-in catalog
- File errors: Show user-friendly error dialogs
- Qt errors: Log and continue with degraded functionality

---

## Performance Guidelines

### CAD Operations
- Keep geometric calculations under 16ms for smooth interaction
- Use spatial indexing for large scenes
- Cache frequently used calculations

### Memory Management
- Clean up Qt objects explicitly
- Use weak references for cross-object links
- Monitor memory usage in long-running sessions

### Database Queries
- Use indexes for common query patterns
- Cache device catalog in memory
- Batch operations for bulk updates
