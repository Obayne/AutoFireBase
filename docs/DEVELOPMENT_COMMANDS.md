# AutoFire Development Command Sheet

**Date:** October 3, 2025
**Project:** AutoFire - Fire Alarm CAD Application
**Environment:** Windows PowerShell + VS Code

---

## 🚀 Quick Start Development Commands

### 1. Initial Project Setup (One-time)
```powershell
# Navigate to project directory
cd C:\Dev\Autofire

# Run automated development setup
.\setup_dev.ps1

# Verify setup
python --version  # Should be 3.11+
python -c "import PySide6; print('PySide6 OK')"
```

### 2. Daily Development Workflow

#### Start Development Session
```powershell
# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Verify environment
which python  # Should point to .venv/Scripts/python.exe
```

#### Run Application
```powershell
# Development mode (with hot reload)
python main.py

# Debug mode (verbose logging)
python tools/run_app_debug.py

# Headless test mode
python -c "
import sys
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
from frontend.controller import AutoFireController
controller = AutoFireController()
print('Controller created successfully')
"
```

#### Code Quality & Testing
```powershell
# Run all tests
pytest -q

# Run specific test categories
pytest tests/backend/ -v      # Backend tests
pytest tests/cad_core/ -v     # CAD algorithm tests
pytest tests/frontend/ -v     # UI tests

# Code formatting
black .

# Linting
ruff check --fix .

# Type checking
mypy frontend/ backend/ cad_core/

# Full quality check
black . && ruff check --fix . && pytest -q
```

#### Build Commands
```powershell
# Production build
.\Build_AutoFire.ps1

# Debug build
.\Build_AutoFire_Debug.ps1

# Clean build artifacts
.\Build_Clean.ps1

# Run built application
.\dist\AutoFire\AutoFire.exe
.\dist\AutoFire_Debug\AutoFire_Debug.exe
```

---

## 🔧 VS Code Integration Commands

### VS Code Tasks (Add to `.vscode/tasks.json`)
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Setup Dev Environment",
            "type": "shell",
            "command": ".\\setup_dev.ps1",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Run Application",
            "type": "shell",
            "command": "python",
            "args": ["main.py"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "pytest",
            "args": ["-q"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Format Code",
            "type": "shell",
            "command": "black",
            "args": ["."],
            "group": "build"
        },
        {
            "label": "Lint Code",
            "type": "shell",
            "command": "ruff",
            "args": ["check", "--fix", "."],
            "group": "build"
        },
        {
            "label": "Build Production",
            "type": "shell",
            "command": ".\\Build_AutoFire.ps1",
            "group": "build"
        }
    ]
}
```

### VS Code Launch Configurations (Add to `.vscode/launch.json`)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: AutoFire Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "python": "${workspaceFolder}/.venv/Scripts/python.exe"
        },
        {
            "name": "Python: Debug Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tools/run_app_debug.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "python": "${workspaceFolder}/.venv/Scripts/python.exe"
        },
        {
            "name": "Python: Test Current File",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/tests/${fileBasenameNoExtension}.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "python": "${workspaceFolder}/.venv/Scripts/python.exe"
        }
    ]
}
```

### VS Code Settings (Add to `.vscode/settings.json`)
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["-q"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.fixAll.ruff": "explicit",
        "source.organizeImports.ruff": "explicit"
    },
    "files.associations": {
        "*.spec": "python"
    },
    "git.autofetch": true,
    "git.enableSmartCommit": true
}
```

---

## 📊 Git Workflow Commands

### Branch Management
```bash
# Create feature branch
git checkout -b feat/add-new-feature

# Create fix branch
git checkout -b fix/critical-bug

# Create chore branch
git checkout -b chore/update-dependencies

# Push new branch
git push -u origin feat/add-new-feature
```

### Daily Git Workflow
```bash
# Check status
git status

# Stage changes
git add .

# Commit with conventional format
git commit -m "feat: add new device placement tool

- Add DevicePlacementWidget to frontend/widgets/
- Implement drag-drop placement logic
- Add unit tests for placement validation"

# Push changes
git push

# Create pull request (via GitHub UI)
# Or update existing PR
git push
```

### Code Review & Merge
```bash
# Update from main
git checkout main
git pull origin main
git checkout feat/my-feature
git rebase main

# Resolve conflicts if any
# Then force push (only for your own branches)
git push --force-with-lease
```

---

## 🔍 Debugging Commands

### Application Debugging
```powershell
# Run with debug logging
$env:PYTHONPATH = "."
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import main
"

# Test specific components
python -c "
from backend.catalog import load_catalog
catalog = load_catalog()
print(f'Loaded {len(catalog)} devices')
"

# Test CAD algorithms
python -c "
from cad_core.lines import Line
line = Line((0, 0), (10, 10))
print(f'Line length: {line.length()}')
"
```

### Database Debugging
```powershell
# Check database
python -c "
import sqlite3
conn = sqlite3.connect('~/AutoFire/catalog.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print('Tables:', tables)
conn.close()
"

# Reset database
python -c "
import os
db_path = os.path.expanduser('~/AutoFire/catalog.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print('Database reset')
"
```

### Performance Profiling
```powershell
# Profile application startup
python -m cProfile -s time main.py

# Profile specific function
python -c "
import cProfile
from backend.coverage_service import CoverageService
cProfile.run('CoverageService().calculate_coverage([])', sort='time')
"
```

---

## 📦 Dependency Management

### Update Dependencies
```powershell
# Update core dependencies
pip install -r requirements.txt --upgrade

# Update dev dependencies
pip install -r requirements-dev.txt --upgrade

# Update specific package
pip install PySide6 --upgrade

# Check for security vulnerabilities
pip audit
```

### Environment Management
```powershell
# Recreate virtual environment
Remove-Item .venv -Recurse -Force
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Export current environment
pip freeze > requirements-current.txt
```

---

## 🚀 Deployment Commands

### Local Testing of Builds
```powershell
# Test production build
.\Build_AutoFire.ps1
.\dist\AutoFire\AutoFire.exe

# Test debug build
.\Build_AutoFire_Debug.ps1
.\dist\AutoFire_Debug\AutoFire_Debug.exe
```

### Release Preparation
```powershell
# Update version
echo "1.2.4" > VERSION.txt

# Update changelog
# Edit CHANGELOG.md with new version notes

# Create git tag
git add VERSION.txt CHANGELOG.md
git commit -m "chore: prepare release v1.2.4"
git tag -a v1.2.4 -m "Release v1.2.4: Add new features"
git push origin v1.2.4

# Build final release
.\Build_AutoFire.ps1
```

---

## 🔧 Maintenance Commands

### Code Quality Maintenance
```powershell
# Full code quality check
black --check .
ruff check .
mypy frontend/ backend/ cad_core/
pytest --cov=. --cov-report=term-missing

# Auto-fix issues
black .
ruff check --fix .
```

### Repository Maintenance
```powershell
# Clean untracked files
git clean -fd

# Update pre-commit hooks
pre-commit autoupdate

# Check repository health
git fsck
git gc --prune=now
```

### Log Analysis
```powershell
# View recent logs
Get-ChildItem logs/ -Name | Sort-Object -Descending | Select-Object -First 5

# Analyze log file
Get-Content logs/autofire_20251003.log | Select-String -Pattern "ERROR" -Context 2

# Open logs directory
Open_Logs.cmd
```

---

## ⚡ Quick Reference Aliases (Add to PowerShell Profile)

Add these to `$PROFILE` for quick access:

```powershell
# AutoFire development aliases
function autofire-dev { cd C:\Dev\Autofire; . .venv/Scripts/Activate.ps1 }
function autofire-run { python main.py }
function autofire-test { pytest -q }
function autofire-build { .\Build_AutoFire.ps1 }
function autofire-clean { .\Build_Clean.ps1 }
function autofire-quality { black .; ruff check --fix .; pytest -q }
```

Then use:
```powershell
autofire-dev    # Setup environment
autofire-run    # Run application
autofire-test   # Run tests
autofire-build  # Build application
autofire-quality # Full quality check
```

---

**Note:** All commands assume Windows PowerShell environment. For bash/zsh equivalents, replace `.\` with `./` and adjust paths accordingly.
