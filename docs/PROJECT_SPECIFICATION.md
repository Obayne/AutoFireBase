# AutoFire Project Technical Specification

**Document Version:** 1.0
**Date:** October 3, 2025
**Project:** AutoFire - Fire Alarm CAD Application
**Architecture:** Modular PySide6/Qt Desktop Application

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Entry Points](#entry-points)
4. [Core Architecture Layers](#core-architecture-layers)
5. [Python Files and Classes](#python-files-and-classes)
6. [File Relationships and Dependencies](#file-relationships-and-dependencies)
7. [Development Environment Setup](#development-environment-setup)
8. [Build and Deployment](#build-and-deployment)
9. [Testing Structure](#testing-structure)
10. [Configuration and Settings](#configuration-and-settings)

---

## 1. Project Overview

AutoFire is a Python-based CAD application for fire alarm system design, built with PySide6 (Qt for Python). The application features multi-window CAD tools, device placement, coverage analysis, and DXF import/export capabilities.

**Key Technologies:**
- **GUI Framework:** PySide6 (Qt6 bindings for Python)
- **CAD Engine:** Custom geometry algorithms in `cad_core/`
- **Database:** SQLite for device catalog storage
- **File Formats:** DXF import/export, PDF reports
- **Build System:** PyInstaller for executable distribution

**Architecture Pattern:** Clean modular architecture with clear separation of concerns across three main layers:
- `frontend/` - UI Layer (PySide6/Qt widgets and windows)
- `backend/` - Business Logic Layer (services, persistence, import/export)
- `cad_core/` - CAD Algorithms Layer (geometry, tools, calculations)

---

## 2. Project Structure

### Root Directory Structure

```
C:\Dev\Autofire\
├── main.py                          # Primary application entry point
├── frontend/                        # UI Layer (PySide6/Qt)
├── backend/                         # Business Logic Layer
├── cad_core/                        # CAD Algorithms Layer
├── tests/                          # Test suite
├── docs/                           # Documentation
├── app/                            # Legacy application code (being migrated)
├── tools/                          # Development and utility tools
├── scripts/                        # Build and automation scripts
├── requirements.txt                # Core dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Python project configuration
├── setup_dev.ps1                   # Development environment setup
├── Build_AutoFire.ps1              # Production build script
├── Build_AutoFire_Debug.ps1        # Debug build script
├── AutoFire.spec                   # PyInstaller specification (production)
├── AutoFire_Debug.spec             # PyInstaller specification (debug)
└── .github/                        # GitHub workflows and templates
```

### Key Directories Detail

#### `/frontend/` - UI Layer
```
frontend/
├── app.py                          # Main Qt application entry point
├── controller.py                   # Application controller (AutoFireController)
├── windows/                        # Main application windows
│   ├── model_space.py             # Model Space Window (CAD drawing)
│   ├── paperspace.py              # Paper Space Window (layouts)
│   ├── project_overview.py        # Project Overview Window
│   └── scene.py                   # GridScene and CanvasView classes
├── dialogs/                       # Modal dialogs
├── ui/                           # Reusable UI components
├── tool_registry.py              # CAD tool registration system
├── wiring.py                     # Wire routing and connection logic
├── device.py                     # Device placement and management
├── coverage.py                   # Coverage analysis overlays
├── assistant.py                  # AI assistant integration
├── settings.py                   # Application settings management
└── qt_shapes.py                  # Qt graphics shape utilities
```

#### `/backend/` - Business Logic Layer
```
backend/
├── catalog.py                     # Device catalog management
├── catalog_store.py               # Catalog data persistence
├── coverage_service.py            # Coverage calculation services
├── ops_service.py                 # CAD operations service
├── geom_repo.py                   # Geometry repository
├── dxf_import.py                  # DXF file import/export
├── logging_config.py              # Logging configuration
├── models.py                      # Data models
└── data/                         # Data persistence interfaces
```

#### `/cad_core/` - CAD Algorithms Layer
```
cad_core/
├── tools/                        # CAD tool implementations
├── arc.py                        # Arc geometry algorithms
├── circle.py                     # Circle geometry algorithms
├── fillet.py                     # Fillet/rounding algorithms
├── geom_adapter.py               # Geometry adapter utilities
├── lines.py                      # Line geometry algorithms
└── units.py                      # Unit conversion utilities
```

#### `/tests/` - Test Suite
```
tests/
├── backend/                      # Backend service tests
├── cad_core/                     # CAD algorithm tests
├── frontend/                     # UI component tests
├── test_*.py                     # Individual test files
└── conftest.py                   # pytest configuration
```

---

## 3. Entry Points

### Primary Entry Points

#### 1. `main.py` - Main Application Entry Point
**Location:** `C:\Dev\Autofire\main.py`
**Purpose:** Clean, cross-platform entry point for the AutoFire application
**Usage:**
```bash
cd C:\Dev\Autofire
python main.py
```

**Code Structure:**
```python
#!/usr/bin/env python3
"""
AutoFire - Fire Alarm CAD Application
Clean entry point following modular architecture.
"""

import os
import sys

# Add current directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from frontend.app import main

if __name__ == "__main__":
    sys.exit(main())
```

#### 2. `frontend/app.py` - Qt Application Entry Point
**Location:** `C:\Dev\Autofire\frontend\app.py`
**Purpose:** Main Qt application with proper error handling and logging
**Usage:** Called by `main.py`, not typically run directly

**Key Functions:**
- `main() -> int` - Application entry point
- Sets up Qt application instance
- Creates AutoFireController
- Handles startup errors gracefully

#### 3. `frontend/controller.py` - Application Controller
**Location:** `C:\Dev\Autofire\frontend\controller.py`
**Purpose:** Main application controller managing multi-window coordination
**Class:** `AutoFireController(QMainWindow)`

### Secondary Entry Points

#### Development and Testing
- `test_app.py` - Basic application startup test
- `tools/run_app_debug.py` - Debug application runner
- `scripts/run_app_debug.py` - Alternative debug runner

#### Build Scripts
- `Build_AutoFire.ps1` - Production build
- `Build_AutoFire_Debug.ps1` - Debug build
- `setup_dev.ps1` - Development environment setup

### PyInstaller Specifications
- `AutoFire.spec` - Production executable build configuration
- `AutoFire_Debug.spec` - Debug executable build configuration

---

## 4. Core Architecture Layers

### Frontend Layer (`/frontend/`)

**Purpose:** User interface and interaction handling
**Framework:** PySide6 (Qt6 for Python)
**Key Components:**

1. **AutoFireController** (`controller.py`)
   - Main application coordinator
   - Manages window lifecycle
   - Coordinates between UI and backend

2. **Application Windows** (`windows/`)
   - `ModelSpaceWindow` - CAD drawing canvas
   - `PaperspaceWindow` - Layout and documentation
   - `ProjectOverviewWindow` - Project management

3. **UI Components**
   - `GridScene` & `CanvasView` - CAD drawing surface
   - Dialogs for device placement, wire routing, etc.
   - Tool registry for CAD operations

### Backend Layer (`/backend/`)

**Purpose:** Business logic, data persistence, and services
**Key Components:**

1. **Catalog System**
   - `catalog.py` - Device catalog management
   - `catalog_store.py` - SQLite persistence

2. **Services**
   - `coverage_service.py` - Coverage calculations
   - `ops_service.py` - CAD operations
   - `geom_repo.py` - Geometry data management

3. **Import/Export**
   - `dxf_import.py` - DXF file handling

### CAD Core Layer (`/cad_core/`)

**Purpose:** Geometry algorithms and CAD calculations
**Key Components:**

1. **Geometric Primitives**
   - `lines.py` - Line segment algorithms
   - `arc.py` - Arc geometry
   - `circle.py` - Circle geometry
   - `fillet.py` - Corner rounding

2. **Tools** (`tools/`)
   - CAD operation implementations
   - Trim, extend, array tools

3. **Utilities**
   - `units.py` - Unit conversions
   - `geom_adapter.py` - Geometry adapters

---

## 5. Python Files and Classes

### Major Classes by Category

#### Application Controllers
- `AutoFireController` (`frontend/controller.py`) - Main app coordinator
- `ModelSpaceWindow` (`frontend/windows/model_space.py`) - CAD drawing window
- `PaperspaceWindow` (`frontend/windows/paperspace.py`) - Layout window
- `ProjectOverviewWindow` (`frontend/windows/project_overview.py`) - Project management

#### UI Components
- `GridScene` (`frontend/windows/scene.py`) - CAD drawing surface with grid
- `CanvasView` (`frontend/windows/scene.py`) - Qt graphics view for CAD
- `WireSpoolDialog` (`app/dialogs/wire_spool.py`) - Wire management dialog

#### CAD Tools
- `ArrayTool` (`tools/apply_inline_050_cadA.py`) - Array placement tool
- `CoverageDialog` (`tools/apply_inline_050_cadA.py`) - Coverage analysis dialog
- `DeviceItem` (`tools/apply_inline_050_cadA.py`) - CAD device representation

#### Backend Services
- Catalog management classes in `backend/catalog.py`
- Coverage calculation classes in `backend/coverage_service.py`
- DXF import/export classes in `backend/dxf_import.py`

#### Test Classes
- `TestTrimTool` (`tests/test_trim_tool.py`)
- `TestOSNAP` (`tests/test_osnap.py`)
- `TestMoveTool` (`tests/test_move_tool.py`)
- `TestDXFImport` (`tests/test_dxf_import.py`)

### Key Functions

#### Main Functions
- `main()` in `frontend/app.py` - Qt application entry point
- `main()` in `main.py` - Cross-platform application launcher

#### CAD Operations
- Geometry calculation functions in `cad_core/*.py`
- Tool operation functions in `cad_core/tools/`
- Coverage calculation functions in `backend/coverage_service.py`

#### Import/Export
- DXF parsing functions in `backend/dxf_import.py`
- Report generation functions (ReportLab integration)

---

## 6. File Relationships and Dependencies

### Import Hierarchy

#### Frontend Layer Dependencies
```
frontend/app.py
├── PySide6.QtWidgets (QApplication)
└── frontend.controller (AutoFireController)

frontend/controller.py
├── PySide6.Qt* (Qt framework)
├── backend.catalog (load_catalog)
├── backend.logging_config (setup_logging)
└── frontend.windows.* (application windows)
```

#### Backend Layer Dependencies
```
backend/catalog.py
├── sqlite3 (database)
└── backend.models (data models)

backend/dxf_import.py
├── ezdxf (DXF library)
└── shapely (geometry)
```

#### CAD Core Dependencies
```
cad_core/*.py
└── math, typing (standard library)
```

### Data Flow

#### Application Startup
1. `main.py` → `frontend/app.py::main()`
2. `frontend/app.py` → `AutoFireController()`
3. `AutoFireController` → loads catalog, creates windows
4. Windows → initialize CAD scenes and tools

#### CAD Operations
1. User interaction → `CanvasView` event handling
2. `CanvasView` → `GridScene` → CAD tools
3. CAD tools → `cad_core/` algorithms
4. Results → `backend/` services for persistence
5. Updates → UI refresh

#### File Operations
1. DXF import → `backend/dxf_import.py`
2. Device catalog → `backend/catalog.py`
3. Project data → SQLite database (`autofire.db`)

### Database Relationships

#### SQLite Database (`autofire.db`)
- Device catalog tables
- Project data tables
- User preferences
- Managed by `backend/catalog_store.py`

#### File Format Dependencies
- **DXF Files:** Parsed by `ezdxf` library in `backend/dxf_import.py`
- **PDF Reports:** Generated by `reportlab` library
- **Project Files:** JSON format (`autofire.json`)

---

## 7. Development Environment Setup

### Prerequisites
- **Python:** 3.11+ (configured in `pyproject.toml`)
- **Git:** For version control
- **PowerShell:** For build scripts (Windows)

### Automated Setup
**Script:** `setup_dev.ps1`
**Usage:**
```powershell
.\setup_dev.ps1
```

**What it does:**
1. Creates Python virtual environment (`.venv/`)
2. Installs core dependencies from `requirements.txt`
3. Installs dev tools from `requirements-dev.txt`
4. Sets up pre-commit hooks

### Manual Setup Alternative
```powershell
# Create virtual environment
python -m venv .venv

# Activate environment
. .venv/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit
pre-commit install
```

### Core Dependencies (`requirements.txt`)
```
PySide6          # Qt6 GUI framework
ezdxf           # DXF file handling
reportlab       # PDF report generation
shapely         # Geometry operations
```

### Development Dependencies (`requirements-dev.txt`)
```
pytest          # Testing framework
black           # Code formatting
ruff            # Linting
pre-commit      # Git hooks
mypy            # Type checking
```

---

## 8. Build and Deployment

### Build Scripts

#### Production Build
**Script:** `Build_AutoFire.ps1`
**Output:** `dist/AutoFire/AutoFire.exe`
**Usage:**
```powershell
.\Build_AutoFire.ps1
```

#### Debug Build
**Script:** `Build_AutoFire_Debug.ps1`
**Output:** `dist/AutoFire_Debug/AutoFire_Debug.exe`
**Usage:**
```powershell
.\Build_AutoFire_Debug.ps1
```

### PyInstaller Configuration

#### `AutoFire.spec` - Production Build
```python
# PyInstaller specification for production build
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('autofire.db', '.'), ('docs/', 'docs/')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
```

#### Build Process
1. **Dependency Installation:** PyInstaller, PySide6, project dependencies
2. **Cleanup:** Remove old build artifacts
3. **Analysis:** PyInstaller analyzes `main.py` and dependencies
4. **Build:** Creates standalone executable
5. **Packaging:** Includes required data files (database, docs)

### Distribution
- **Executable:** `AutoFire.exe` (production) or `AutoFire_Debug.exe` (debug)
- **Location:** `dist/AutoFire/` or `dist/AutoFire_Debug/`
- **Included Files:** Qt libraries, Python runtime, project data

---

## 9. Testing Structure

### Test Organization
```
tests/
├── backend/                     # Backend service tests
├── cad_core/                    # CAD algorithm tests
├── frontend/                    # UI component tests
├── conftest.py                  # pytest configuration
└── test_*.py                    # Individual test files
```

### Test Categories

#### Unit Tests
- **CAD Algorithms:** `test_trim_tool.py`, `test_units.py`
- **Backend Services:** `test_coverage_service.py`, `test_db_loader.py`
- **Import/Export:** `test_dxf_import.py`

#### Integration Tests
- **UI Components:** `test_project_overview.py`
- **CAD Tools:** `test_draw_tools.py`, `test_move_tool.py`
- **Object Snap:** `test_osnap.py`

#### End-to-End Tests
- **Application Startup:** `test_headless_startup.py`
- **Full Workflows:** Manual testing scenarios

### Running Tests

#### All Tests
```bash
pytest -q
```

#### Specific Test Categories
```bash
pytest tests/backend/ -v        # Backend tests
pytest tests/cad_core/ -v       # CAD core tests
pytest tests/frontend/ -v       # Frontend tests
```

#### With Coverage
```bash
pytest --cov=. --cov-report=html
# View report in htmlcov/index.html
```

### Test Configuration
**File:** `tests/conftest.py`
**Purpose:** pytest fixtures and configuration
**Key Fixtures:**
- Qt application setup
- Test database initialization
- Mock objects for isolated testing

---

## 10. Configuration and Settings

### Configuration Files

#### `pyproject.toml` - Python Project Configuration
```toml
[tool.black]
line-length = 100
target-version = ["py311"]

[tool.ruff]
line-length = 100
target-version = "py311"
```

#### `requirements.txt` - Core Dependencies
```
PySide6
ezdxf
reportlab
shapely
```

#### `requirements-dev.txt` - Development Dependencies
```
pytest
black
ruff
pre-commit
mypy
```

### Application Settings

#### User Preferences
- **Location:** `~/AutoFire/` directory (user home)
- **Database:** `~/AutoFire/catalog.db`
- **Config Files:** JSON format for user settings

#### Build Configuration
- **PyInstaller Specs:** `AutoFire.spec`, `AutoFire_Debug.spec`
- **Build Scripts:** PowerShell scripts in root directory

### Environment Variables
- **PYTHONPATH:** Automatically managed by entry points
- **QT_QPA_PLATFORM:** May need `windows` for some environments
- **PATH:** Includes virtual environment `Scripts/` directory

---

## Usage Guide

### Starting the Application

#### Development Mode
```bash
cd C:\Dev\Autofire
. .venv/Scripts/Activate.ps1  # Activate virtual environment
python main.py               # Start application
```

#### Production Mode
```bash
# After building with Build_AutoFire.ps1
.\dist\AutoFire\AutoFire.exe
```

### Development Workflow

1. **Setup Environment:** Run `.\setup_dev.ps1`
2. **Make Changes:** Edit Python files in appropriate layer
3. **Run Tests:** `pytest -q` to verify changes
4. **Format Code:** `black .` and `ruff check --fix .`
5. **Test Application:** `python main.py`
6. **Commit:** Follow conventional commit format

### Troubleshooting

#### Common Issues
- **Qt Import Errors:** Ensure PySide6 is installed in virtual environment
- **Database Errors:** Check `~/AutoFire/catalog.db` permissions
- **Build Failures:** Ensure OneDrive sync is paused, try `Build_Clean.ps1`

#### Debug Tools
- **Debug Build:** Use `Build_AutoFire_Debug.ps1` for verbose logging
- **Test Scripts:** `tools/run_app_debug.py` for development testing
- **Log Files:** Check `logs/` directory for application logs

---

**Document Maintenance:** This specification should be updated whenever the project structure or key files change. Reference `docs/MASTER_SPECIFICATION.rtf` for product vision and `docs/DEVELOPMENT_WORKFLOW.md` for development processes.
