# CI Testing Guide

This document describes how to run tests in CI/CD environments and locally.

## Test Categories

AutoFire tests are organized into two categories:

1. **Non-GUI Tests** - Pure logic tests that don't require PySide6 or Qt
2. **GUI Tests** - Tests marked with `@pytest.mark.gui` that require PySide6/Qt

## Running Tests

### CI Environment (Headless, No PySide6)

For CI environments where PySide6 is not installed (e.g., lightweight runners):

```bash
# Install minimal dependencies
pip install pytest black ruff

# Run only non-GUI tests
pytest -m "not gui"
```

This will run all tests except those marked with `@pytest.mark.gui`, avoiding PySide6 dependency.

### CI Environment (With PySide6)

For CI environments with GUI support:

```bash
# Install full dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Set headless mode
export QT_QPA_PLATFORM=offscreen

# Run all tests including GUI
pytest
```

### Local Development

```bash
# Activate virtual environment
. .venv/Scripts/Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate      # Linux/Mac

# Run all tests
pytest

# Run only GUI tests
pytest -m gui

# Run only non-GUI tests
pytest -m "not gui"

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_units.py
```

## Test Markers

Tests are marked using pytest markers:

- `@pytest.mark.gui` - Requires PySide6/Qt, imports GUI modules

Example:
```python
import pytest
from PySide6 import QtWidgets

@pytest.mark.gui
def test_my_gui_feature(qapp, qtbot):
    # Test code that uses Qt
    pass
```

## Pre-commit Checks

Before committing, ensure code passes quality checks:

```bash
# Run pre-commit hooks
pre-commit run --all-files

# Or manually
ruff check --fix .
black .
```

## Test Fixtures

Common fixtures available:

- `qapp` - QApplication instance (skips if PySide6 not available)
- `qtbot` - pytest-qt fixture for GUI testing
- `skip_if_no_qt` - Fixture to skip test if PySide6 not available
- `app_controller` - Mock AutoFire controller for testing

## Current Test Status

As of the latest update:
- **53 non-GUI tests** pass without PySide6
- **GUI tests** require PySide6 and run separately

## Notes

- The root `conftest.py` makes PySide6 optional by conditionally importing it
- Tests marked with `@pytest.mark.gui` that import PySide6 at module level will fail to import without PySide6
- In CI without PySide6, use `-m "not gui"` to exclude GUI tests
- The `QT_QPA_PLATFORM=offscreen` environment variable enables headless GUI testing
