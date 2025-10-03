# Development Setup Guide

This guide provides comprehensive instructions for setting up a development environment for AutoFire.

## Prerequisites

### Required Software
- **Python 3.11+** (recommended: 3.11.x)
- **Git** (2.30+ recommended)
- **PowerShell** (Windows) or compatible shell
- **Visual Studio Code** (recommended editor)

### System Requirements
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB for repository + dependencies
- **Display**: 1920x1080 minimum resolution

## 🚀 Quick Setup (Windows)

### 1. Clone Repository
```powershell
git clone https://github.com/Obayne/AutoFireBase.git
cd AutoFireBase
```

### 2. Run Setup Script
```powershell
# This creates .venv, installs dependencies, and sets up pre-commit hooks
.\setup_dev.ps1
```

### 3. Activate Environment
```powershell
# Always activate before development
. .venv/Scripts/Activate.ps1
```

### 4. Verify Installation
```powershell
# Check Python version
python --version
# Should show: Python 3.11.x

# Check key dependencies
python -c "import PySide6; print('PySide6 OK')"
python -c "import sqlite3; print('SQLite OK')"
```

### 5. Run Application
```powershell
python main.py
```

## 🔧 Manual Setup (Alternative)

If the automated setup fails, follow these manual steps:

### Create Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
. .venv/Scripts/Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip
```

### Install Dependencies
```powershell
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Optional: Install all dev dependencies
pip install -r requirements-dev-minimal.txt
```

### Setup Pre-commit Hooks
```powershell
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install
```

## 🧪 Testing Setup

### Run Test Suite
```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=frontend --cov=backend --cov=cad_core --cov-report=html

# Run specific test file
pytest tests/test_frontend/test_app.py

# Run tests in verbose mode
pytest -v
```

### Test Configuration
- Tests use `pytest` framework
- Coverage reports generated in `htmlcov/`
- Mock Qt components for headless testing
- Database tests use temporary files

## 🛠️ Development Tools

### Code Quality
```powershell
# Format code
black .

# Lint and fix issues
ruff check --fix .

# Sort imports
ruff check --select I --fix .

# Type checking (if mypy configured)
mypy frontend/ backend/ cad_core/
```

### Pre-commit Hooks
The following checks run automatically on commit:
- Ruff linting and import sorting
- Black code formatting
- Trailing whitespace removal
- End-of-file fixes

### IDE Configuration

#### Visual Studio Code
Recommended extensions:
- Python (Microsoft)
- Pylance
- Ruff
- Black Formatter
- Qt for Python

#### VS Code Settings (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

## 🏗️ Building

### Development Builds
```powershell
# Standard release build
.\Build_AutoFire.ps1

# Debug build (with console)
.\Build_AutoFire_Debug.ps1

# Clean build artifacts
.\Build_Clean.ps1
```

### Build Artifacts
- Executables created in `dist/` directory
- Build cache in `build/` directory
- Both directories ignored by git

## 📊 Database Setup

### Device Catalog
The application uses SQLite databases stored in `~/AutoFire/`:

- `catalog.db`: Device catalog with 25K+ fire alarm devices
- `preferences.json`: User preferences and settings

### Database Management
```powershell
# Check database integrity
python check_db.py

# Reset catalog (if needed)
# Delete ~/AutoFire/catalog.db and restart app
```

## 🔧 Troubleshooting

### Common Issues

#### Virtual Environment Issues
```powershell
# Recreate virtual environment
deactivate
Remove-Item .venv -Recurse -Force
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

#### Qt/PySide6 Issues
```powershell
# Reinstall PySide6
pip uninstall PySide6
pip install PySide6

# Check Qt installation
python -c "import PySide6.QtWidgets; print('Qt OK')"
```

#### Import Errors
```powershell
# Ensure you're in the correct directory
cd C:\Dev\Autofire

# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall in development mode
pip install -e .
```

#### Database Errors
```powershell
# Check permissions on ~/AutoFire/
dir "$env:USERPROFILE\AutoFire"

# Reset database
Remove-Item "$env:USERPROFILE\AutoFire\*.db"
```

### Debug Mode
```powershell
# Run with debug output
$env:QT_DEBUG_PLUGINS=1
python main.py

# Check logs
type "$env:USERPROFILE\AutoFire\logs\autofire.log"
```

## 🚀 Advanced Setup

### Multiple Python Versions
```powershell
# Use pyenv or conda for multiple Python versions
pyenv install 3.11.8
pyenv local 3.11.8

# Or with conda
conda create -n autofire python=3.11
conda activate autofire
```

### Development Scripts
Create custom PowerShell scripts in the root directory:

```powershell
# dev.ps1 - Quick development setup
. .venv/Scripts/Activate.ps1
Write-Host "AutoFire development environment ready" -ForegroundColor Green
```

### Remote Development
For remote development (WSL, Docker, etc.):
```bash
# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Set display for GUI applications
export DISPLAY=:0

# Run application
python main.py
```

## 📚 Learning Resources

### Architecture Understanding
- `docs/ARCHITECTURE.md`: Detailed architecture documentation
- `AGENTS.md`: Development principles and guidelines
- `docs/API_REFERENCE.md`: Complete API documentation

### Code Examples
- `tests/`: Test files showing usage patterns
- `Projects/`: Sample project files
- `scripts/`: Utility scripts and tools

### Getting Help
- Check existing GitHub issues
- Review `RECOVERY.md` for common fixes
- See `CLEANUP_PROCEDURE.md` for maintenance procedures

## 🔄 Updating

### Update Dependencies
```powershell
# Update all packages
pip install --upgrade -r requirements.txt

# Update development tools
pip install --upgrade black ruff pre-commit pytest

# Update pre-commit hooks
pre-commit autoupdate
```

### Repository Updates
```powershell
# Sync with upstream
git fetch origin
git merge origin/main

# Update virtual environment
pip install -r requirements.txt
```

## 📋 Checklist

Before starting development:
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Pre-commit hooks installed
- [ ] Application runs (`python main.py`)
- [ ] Tests pass (`pytest`)
- [ ] Code formatting works (`black .` and `ruff check --fix .`)

Happy coding! 🎉
