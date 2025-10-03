# AutoFireBase

**AutoFire** is a Python-based CAD application for fire alarm system design, featuring multi-window CAD tools, device placement, coverage analysis, and DXF import/export capabilities.

## 📋 Master Specification

**🎯 [MASTER SCOPE OF WORK](docs/MASTER_SPECIFICATION.rtf)** - Complete product vision, GUI design, workflow, calculations, and feature specifications for AutoFire Design Suite. This document serves as the authoritative reference for all development work.

## 🏗️ Architecture

AutoFire follows a clean modular architecture with clear separation of concerns:

### Directory Structure
```
AutoFireBase/
├── frontend/          # UI Layer (PySide6/Qt)
│   ├── windows/       # Main application windows
│   ├── dialogs/       # Modal dialogs and forms
│   ├── ui/           # Reusable UI components
│   ├── controller.py # Application controller
│   └── app.py        # Qt application entry point
├── backend/          # Business Logic Layer
│   ├── catalog.py    # Device catalog management
│   ├── logging_config.py # Logging configuration
│   ├── data/         # Data persistence interfaces
│   └── dxf_import.py # File import/export services
├── cad_core/         # CAD Algorithms Layer
│   ├── tools/        # CAD tools and operations
│   └── units.py      # Unit conversion utilities
├── db/              # Database Layer
├── tests/           # Test suite
├── docs/            # Documentation
└── main.py          # Clean application entry point
```

### Key Components

- **Model Space Window**: Primary CAD workspace for device placement and design
- **Paperspace Window**: Print layout and documentation workspace
- **Project Overview Window**: Project management, notes, and AI assistance
- **Device Catalog**: SQLite-backed catalog of 25K+ fire alarm devices
- **CAD Tools**: Draw, modify, measure, snap, and analysis tools
- **DXF Integration**: Import/export capabilities for industry standards

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (recommended)
- Git
- PowerShell (Windows) or compatible shell

### Setup (Windows)
```powershell
# Clone the repository
git clone https://github.com/Obayne/AutoFireBase.git
cd AutoFireBase

# Setup development environment
.\setup_dev.ps1

# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Run the application
python main.py
```

### Alternative Run Methods
```bash
# Using batch file
run_autofire.bat

# Using PowerShell script
.\run_autofire.ps1

# Direct Python execution
python main.py
```

## 🛠️ Development Workflow

### Daily Development
```bash
# Activate environment
. .venv/Scripts/Activate.ps1

# Sync with remote
git pull

# Make changes...

# Format and lint
ruff check --fix .
black .

# Test changes
python main.py

# Commit (pre-commit hooks will run automatically)
git add -A
git commit -m "feat: your feature description"
git push
```

### Code Quality
- **Formatting**: Black (100 char line length)
- **Linting**: Ruff (Python 3.11+ target)
- **Pre-commit**: Automatic formatting/linting on commit
- **Testing**: pytest suite in `tests/`

### Branching Strategy
- `main`: Production-ready code
- `feat/<name>`: New features
- `fix/<name>`: Bug fixes
- `chore/<name>`: Maintenance tasks

## 📦 Build & Distribution

### Building Executables
```powershell
# Release build
.\Build_AutoFire.ps1

# Debug build (with console)
.\Build_AutoFire_Debug.ps1
```

### Build Artifacts
- PyInstaller specs: `AutoFire.spec`, `AutoFire_Debug.spec`
- Output: `dist/` directory (ignored in git)
- Clean builds: `.\Build_Clean.ps1`

## 🔧 Configuration

### Preferences
User preferences are stored in `~/AutoFire/preferences.json`:
```json
{
  "px_per_ft": 12.0,
  "grid": 12,
  "snap": true,
  "show_coverage": true,
  "page_size": "Letter",
  "theme": "dark",
  "units": "Imperial (feet)"
}
```

### Device Database
- Location: `~/AutoFire/catalog.db`
- Schema: SQLite with device specifications
- Management: `check_db.py` for diagnostics

## 🧪 Testing

```bash
# Run full test suite
pytest

# Run specific tests
pytest tests/test_frontend/

# Run with coverage
pytest --cov=frontend --cov=cad_core --cov=backend
```

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
