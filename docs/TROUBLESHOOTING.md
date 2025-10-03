# Troubleshooting Guide

This guide helps diagnose and resolve common issues encountered during AutoFire development and usage.

## 🚨 Quick Diagnosis

### Application Won't Start
```powershell
# Check Python environment
python --version
python -c "import PySide6; print('PySide6 OK')"

# Check database
python check_db.py

# Check logs
type "$env:USERPROFILE\AutoFire\logs\autofire.log"
```

### GUI Not Appearing
```powershell
# Check display environment
echo $env:DISPLAY

# Test Qt installation
python -c "from PySide6.QtWidgets import QApplication; app = QApplication([]); print('Qt OK')"
```

## 🔧 Common Issues & Solutions

### 1. Import Errors

#### Module Not Found
**Symptoms**: `ImportError: No module named 'frontend'`
**Cause**: Running from wrong directory or missing `__init__.py`
**Solution**:
```powershell
# Ensure correct working directory
cd C:\Dev\Autofire

# Check file structure
Get-ChildItem -Recurse -Name | Select-String "__init__.py"

# Reinstall in development mode
pip install -e .
```

#### PySide6 Not Found
**Symptoms**: `ImportError: No module named 'PySide6'`
**Cause**: Missing or corrupted installation
**Solution**:
```powershell
# Reinstall PySide6
pip uninstall PySide6
pip install PySide6

# Check installation
python -c "import PySide6.QtCore; print(PySide6.QtCore.__version__)"
```

### 2. Database Issues

#### Catalog Not Loading
**Symptoms**: Empty device catalog, application starts but no devices available
**Cause**: Database corruption or missing catalog.db
**Solution**:
```powershell
# Check database location
$autofireDir = "$env:USERPROFILE\AutoFire"
if (!(Test-Path $autofireDir)) { New-Item -ItemType Directory -Path $autofireDir }

# Reset catalog
Remove-Item "$autofireDir\catalog.db" -ErrorAction SilentlyContinue

# Restart application to recreate catalog
python main.py
```

#### SQLite Errors
**Symptoms**: `sqlite3.OperationalError` or database lock errors
**Cause**: File permissions or concurrent access
**Solution**:
```powershell
# Check permissions
icacls "$env:USERPROFILE\AutoFire"

# Close other instances
# Ensure no other processes are using the database

# Reset database
python -c "import os; os.remove(os.path.expanduser('~/AutoFire/catalog.db'))"
```

### 3. Qt/GUI Issues

#### Windows Not Appearing
**Symptoms**: Application starts but no windows visible
**Cause**: Qt platform plugin issues or display problems
**Solution**:
```powershell
# Set Qt platform
$env:QT_QPA_PLATFORM = "windows"

# Debug Qt plugins
$env:QT_DEBUG_PLUGINS = 1
python main.py

# Check Qt installation
python -c "from PySide6.QtWidgets import QApplication, QLabel; app = QApplication([]); label = QLabel('Test'); label.show(); app.exec()"
```

#### High DPI Issues
**Symptoms**: Blurry text or incorrect scaling
**Cause**: Display scaling not handled properly
**Solution**:
```powershell
# Enable high DPI scaling
$env:QT_ENABLE_HIGHDPI_SCALING = 1
$env:QT_SCALE_FACTOR = 1.0
python main.py
```

### 4. Build Issues

#### PyInstaller Failures
**Symptoms**: Build scripts fail with import errors
**Cause**: Missing dependencies or path issues
**Solution**:
```powershell
# Clean build artifacts
.\Build_Clean.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Check PyInstaller
pip install --upgrade PyInstaller

# Run build
.\Build_AutoFire.ps1
```

#### Executable Won't Run
**Symptoms**: Built .exe fails to start
**Cause**: Missing DLLs or Qt plugins
**Solution**:
```powershell
# Check executable dependencies
# Use tools like Dependency Walker or Process Monitor

# Rebuild with debug information
.\Build_AutoFire_Debug.ps1

# Check Qt plugins in dist directory
Get-ChildItem dist\ -Recurse | Select-String "platforms"
```

### 5. Performance Issues

#### Slow Startup
**Symptoms**: Application takes >30 seconds to start
**Cause**: Large catalog loading or slow database queries
**Solution**:
```powershell
# Profile startup
python -c "
import cProfile
import main
cProfile.run('main.main()', 'profile.prof')
"

# Optimize database queries
# Check indexes in catalog.db

# Reduce catalog size for development
# Modify backend/catalog.py to limit loaded devices
```

#### UI Freezing
**Symptoms**: Interface becomes unresponsive during operations
**Cause**: Long-running operations on main thread
**Solution**:
```powershell
# Move heavy operations to background threads
# Use QThread for database operations
# Implement progress dialogs for long operations

# Profile performance
python -m cProfile -s time main.py
```

### 6. Development Environment Issues

#### Pre-commit Hook Failures
**Symptoms**: Commits blocked by linting errors
**Cause**: Code doesn't meet style requirements
**Solution**:
```powershell
# Auto-fix issues
ruff check --fix .
black .

# Check what pre-commit is doing
pre-commit run --all-files

# Bypass hooks for urgent commits
git commit --no-verify -m "urgent: fix description"
```

#### Test Failures
**Symptoms**: `pytest` fails with import or Qt errors
**Cause**: Test environment not properly configured
**Solution**:
```powershell
# Run tests with Qt mocking
pytest --tb=short

# Check test configuration
pytest --collect-only

# Run specific test
pytest tests/test_frontend/test_app.py -v
```

## 🐛 Debugging Techniques

### Logging
```powershell
# Enable debug logging
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
import main
main.main()
"

# Check application logs
type "$env:USERPROFILE\AutoFire\logs\autofire.log"
```

### Qt Debugging
```powershell
# Enable Qt debug output
$env:QT_LOGGING_RULES = "qt.*=true"
$env:QT_DEBUG_PLUGINS = 1
python main.py
```

### Python Debugging
```powershell
# Use pdb for debugging
python -m pdb main.py

# Add debug prints
# Modify code to add logging statements
```

### Memory Debugging
```powershell
# Check memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

## 🔄 Recovery Procedures

### Complete Reset
```powershell
# Stop all Python processes
Stop-Process -Name python -ErrorAction SilentlyContinue

# Clean virtual environment
deactivate
Remove-Item .venv -Recurse -Force
python -m venv .venv
. .venv/Scripts/Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Reset user data
Remove-Item "$env:USERPROFILE\AutoFire" -Recurse -Force

# Restart application
python main.py
```

### Git Recovery
```powershell
# Reset to clean state
git reset --hard HEAD
git clean -fd

# Reapply setup
.\setup_dev.ps1
```

## 📞 Getting Help

### Information to Provide
When reporting issues, include:
- Operating system and version
- Python version (`python --version`)
- Full error traceback
- Steps to reproduce
- Recent changes made
- Log files from `~/AutoFire/logs/`

### Support Resources
- **GitHub Issues**: Check existing issues and create new ones
- **RECOVERY.md**: Common recovery procedures
- **CLEANUP_PROCEDURE.md**: Maintenance and cleanup steps
- **docs/ARCHITECTURE.md**: Understanding the codebase
- **docs/API_REFERENCE.md**: API documentation

### Emergency Contacts
- Check `CODEOWNERS` for maintainers
- Review `TEAM.md` for team contacts

## 🚨 Critical Issues

### Data Loss
**Symptoms**: Project files corrupted or missing
**Solution**:
```powershell
# Check backups
Get-ChildItem backup_current\

# Restore from git (if committed)
git checkout HEAD -- Projects/

# Contact team for backup restoration
```

### System Instability
**Symptoms**: System crashes or hangs
**Solution**:
- Close AutoFire immediately
- Check system resources
- Update graphics drivers
- Disable hardware acceleration if needed

### Security Issues
**Symptoms**: Unexpected network activity or file access
**Solution**:
- Disconnect from network
- Scan with antivirus
- Check running processes
- Report to security team immediately

---

## 📋 Quick Reference

### Essential Commands
```powershell
# Environment
. .venv/Scripts/Activate.ps1
python --version

# Development
python main.py
pytest
black .
ruff check --fix .

# Building
.\Build_AutoFire.ps1
.\Build_Clean.ps1

# Database
python check_db.py

# Logs
type "$env:USERPROFILE\AutoFire\logs\autofire.log"
```

### File Locations
- **Application**: `C:\Dev\Autofire\`
- **User Data**: `$env:USERPROFILE\AutoFire\`
- **Logs**: `$env:USERPROFILE\AutoFire\logs\`
- **Database**: `$env:USERPROFILE\AutoFire\catalog.db`
- **Preferences**: `$env:USERPROFILE\AutoFire\prefs.json`

Remember: When in doubt, check the logs first! 📋
