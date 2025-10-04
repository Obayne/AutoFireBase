# AutoFire Design Suite

**AutoFire** is a professional CAD application for fire alarm system design, featuring System Builder staging, device placement, circuit management, and compliance validation. Currently in active development with core CAD infrastructure and fire alarm circuit logic implemented.

## 📋 Master Specification & Current Status

**🎯 [MASTER SPECIFICATION](AutoFire_Full_Spec.rtf)** - Complete product vision with 17 sections covering GUI design, workflow, calculations, and feature specifications.

**📊 [COMPLIANCE AUDIT](MASTER_SPEC_COMPLIANCE.md)** - Detailed assessment of current implementation vs specification:
- ✅ **6/17 sections fully implemented** (35%)
- 🟡 **8/17 sections partially implemented** (47%)
- ❌ **3/17 sections not implemented** (18%)

**Current Version**: 0.8.0 - Core foundation with System Builder, device placement, and fire alarm circuits

## 🏗️ Architecture

AutoFire follows a clean modular architecture with clear separation of concerns, implementing professional fire alarm CAD workflows.

### Directory Structure
```
AutoFire/
├── frontend/          # UI Layer (PySide6/Qt)
│   ├── windows/       # Main application windows (Model Space)
│   │   ├── model_space.py    # Primary CAD workspace (1587 lines)
│   │   └── scene.py          # Canvas interaction & device placement
│   ├── panels/        # Dockable panels and specialized widgets
│   │   ├── staging_system_builder.py # System Builder staging (655 lines)
│   │   └── layer_manager.py          # Layer visibility & management
│   ├── fire_alarm_panel.py   # FACP with NAC/SLC circuits (167 lines)
│   ├── circuit_manager.py    # Visual wire system with color coding
│   ├── device.py            # Enhanced device items with circuit properties
│   └── app.py               # Qt application entry point
├── backend/          # Business Logic Layer
│   ├── catalog.py    # Device catalog with 7 fire alarm devices
│   ├── models.py     # Data models for persistence
│   ├── logging_config.py # Professional logging configuration
│   └── dxf_import.py # DXF import services
├── cad_core/         # CAD Algorithms Layer
│   ├── commands.py   # Command pattern for undo/redo
│   ├── tools/        # CAD tools and drawing operations
│   └── units.py      # Unit conversion utilities
├── tests/           # Comprehensive test suite
│   ├── frontend/    # UI component tests
│   ├── backend/     # Business logic tests
│   └── cad_core/    # Algorithm tests
├── docs/            # Architecture and API documentation
├── app/main.py      # Primary development entry point
└── AutoFire.spec    # PyInstaller build specification
```

### Key Components Implemented

- **Model Space Window**: Professional CAD workspace with device palette, wire spool, inspector tabs
- **System Builder**: Complete staging warehouse for panels, devices, wire, and policies (per spec section 3)
- **Fire Alarm Panel**: Main FACP with NAC/SLC circuit management and visual terminals
- **Circuit Manager**: Color-coded wire system (NAC=red, SLC=blue, Power=black) with validation
- **Device Catalog**: SQLite-backed catalog of fire alarm devices with proper type mapping
- **CAD Command Stack**: Professional undo/redo with command pattern implementation
- **Layer Management**: Proper layer visibility, locking, and organization

### Core Workflows Operational

✅ **System Builder Staging**: Full staging warehouse per specification
✅ **Device Placement**: Professional placement with inspector properties
✅ **Circuit Management**: Fire alarm circuit validation and device assignment
✅ **Wire Routing**: Visual wire system with proper color coding
✅ **Panel Integration**: Main FACP as power source with circuit terminals

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (recommended)
- Git
- PowerShell (Windows) or compatible shell

### Development Setup (Windows)
```powershell
# Clone repository
git clone https://github.com/your-org/AutoFire.git
cd AutoFire

# Run setup script (creates venv, installs deps, configures pre-commit)
.\setup_dev.ps1

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run application
python app\main.py
```

### Build Executable
```powershell
# Build release version
.\Build_AutoFire.ps1

# Build debug version with console
.\Build_AutoFire_Debug.ps1
```

### Run Tests
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run full test suite
pytest -q

# Run specific test categories
pytest tests/frontend/ -v      # UI tests
pytest tests/cad_core/ -v      # Algorithm tests
pytest tests/backend/ -v       # Business logic tests
```

## 🛠️ Development Workflow

### Daily Development
```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Run application for testing
python app\main.py

# Format and lint before commit
ruff check --fix .
black .

# Run tests
pytest -q

# Commit (pre-commit hooks will run automatically)
git add -A
git commit -m "feat: your feature description"
git push
```

### Code Quality Standards
- **Formatting**: Black (100 char line length per `pyproject.toml`)
- **Linting**: Ruff (Python 3.11+ target)
- **Pre-commit**: Automatic formatting/linting on commit via `setup_dev.ps1`
- **Testing**: Comprehensive pytest suite in `tests/`

### Branching Strategy (per AGENTS.md)
- `main`: Production-ready code (keep green)
- `feat/<name>`: New features (≤300 line focused changes)
- `fix/<name>`: Bug fixes
- `chore/<name>`: Maintenance tasks

## 📦 Build & Distribution

### Building Executables
```powershell
# Release build (using AutoFire.spec)
.\Build_AutoFire.ps1

# Debug build with console (using AutoFire_Debug.spec)
.\Build_AutoFire_Debug.ps1

# Clean build artifacts
.\Build_Clean.ps1
```

### Build System
- **PyInstaller**: `AutoFire.spec` and `AutoFire_Debug.spec` for packaging
- **Output**: `dist/` directory (git ignored)
- **Dependencies**: Handled via requirements.txt and venv

## 🧪 Testing Strategy

### Test Coverage
```powershell
# Run full test suite
pytest -q

# Specific test categories
pytest tests/frontend/ -v      # UI components (model_space, dialogs)
pytest tests/cad_core/ -v      # CAD algorithms (drawing, geometry)
pytest tests/backend/ -v       # Business logic (catalog, models)

# Run with coverage reporting
pytest --cov=frontend --cov=cad_core --cov=backend
```

### Test Organization
- `tests/frontend/` - UI component tests
- `tests/cad_core/` - Algorithm and geometry tests
- `tests/backend/` - Business logic and data tests
- Test fixtures in `conftest.py` for shared setup

## 🔧 Configuration & Data

### User Preferences (`autofire.json`)
```json
{
  "px_per_ft": 12.0,
  "grid": 12,
  "snap": true,
  "show_coverage": true,
  "theme": "dark",
  "units": "Imperial"
}
```

### Device Database (`autofire.db`)
- **SQLite database** with 7 fire alarm devices
- **Schema**: Managed by `backend/models.py`
- **Diagnostics**: Use `check_db.py` for database inspection
- **Rebuild**: `rebuild_db.py` for fresh initialization

## 🚦 Current Status & Next Steps

### What's Working (Core Foundation)
- ✅ Professional CAD interface with proper Qt docking
- ✅ System Builder staging workflow per specification
- ✅ Device placement with fire alarm panel integration
- ✅ Circuit management with color-coded wires
- ✅ Inspector panels for device properties
- ✅ Command stack for undo/redo operations

### Priority Development Areas
1. **Live Calculations** - Voltage drop, battery sizing, SLC analysis
2. **Reports & Outputs** - Riser diagrams, cable schedules, BOM
3. **Auto-Addressing** - Automatic device addressing with policy enforcement
4. **Compliance Engine** - NFPA/ADA rule checking with issue reporting

### Contributing
- Reference `AGENTS.md` for repository principles and workflow
- Check `MASTER_SPEC_COMPLIANCE.md` for implementation status
- Follow branching strategy: small focused changes via feature branches
- Ensure tests pass and pre-commit hooks succeed before PR

## 📚 Documentation

- `AGENTS.md`: Development principles and guidelines
- `docs/ARCHITECTURE.md`: Detailed architecture documentation
- `docs/CONTRIBUTING.md`: Contribution guidelines
- `CHANGELOG.md`: Version history and changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make changes following the architecture guidelines
4. Add tests for new functionality
5. Ensure code passes linting: `ruff check --fix . && black .`
6. Commit with clear messages referencing issues
7. Push and create a pull request

### Code Review Process
- All changes require review
- CI must pass (formatting, linting, tests)
- At least one maintainer approval required
- Small, focused PRs preferred

## 📄 License

See LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues
- **Qt/GUI not showing**: Ensure virtual environment is activated
- **Import errors**: Run `pip install -r requirements.txt`
- **Database issues**: Check `~/AutoFire/` directory permissions
- **Build failures**: Clean build artifacts with `.\Build_Clean.ps1`

### Logs
- Application logs: `~/AutoFire/logs/`
- View logs: `.\Open_Logs.cmd`
- Debug mode: Use `Run_AutoFire_Debug.cmd`

### Getting Help
- Check existing issues on GitHub
- Review `RECOVERY.md` for common fixes
- See `CLEANUP_PROCEDURE.md` for maintenance
