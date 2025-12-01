# AutoFireBase

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Qt](https://img.shields.io/badge/Qt-PySide6-green.svg)](https://www.qt.io/qt-for-python)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-pytest-orange.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

> Professional CAD-style desktop application for fire protection system design, built with Python and Qt.

## Overview

AutoFireBase is a Qt-based desktop CAD application specialized for fire protection engineering. Built with Python 3.11 and PySide6, it provides professional drawing tools, DXF import/export, device placement, coverage analysis, and automated wiring generation.

**Version:** 0.4.7
**Platform:** Windows (primary), cross-platform capable
**Architecture:** PySide6 GUI + Custom geometry kernel + SQLite persistence

## Features

### Core CAD Tools

- **Drawing:** Lines, circles, arcs, polylines, freehand, revision clouds
- **Editing:** Move, rotate, scale, mirror, array, trim, extend, chamfer, fillet
- **Dimensions:** Linear, aligned, angular, radial measurements
- **Layers:** Multi-layer management with visibility controls
- **Snapping:** Endpoint, midpoint, center, intersection, perpendicular osnaps

### Fire Protection Specific

- **Device Catalog:** Comprehensive library of fire protection devices
- **Coverage Analysis:** Automated area coverage calculations
- **Wiring:** Intelligent wiring generation between devices
- **BOM Generation:** Automatic bill of materials from design

### Import/Export

- **DXF:** Full import/export support via `ezdxf`
- **PDF:** Underlay support for base drawings
- **Native Format:** `.autofire` project files

### DevOps & Quality Tools

- **Performance Testing:** pytest-benchmark for geometry operations (33 benchmarks)
- **Build Caching:** Smart PyInstaller builds with MD5 change detection (30-60x speedup)
- **Error Tracking:** Sentry SDK integration (5k events/month free tier)
- **Documentation:** Sphinx auto-generated docs with GitHub Pages deployment
- **Remote Access:** VS Code Remote Tunnels for mobile development

## Quick Start

### Prerequisites

- Python 3.11 (recommended)
- Git
- PowerShell (Windows)

### Installation (Windows)

```powershell
# Clone repository
git clone https://github.com/Obayne/AutoFireBase.git
cd AutoFireBase

# Run automated setup (creates .venv, installs deps, sets up pre-commit)
./setup_dev.ps1

# Activate virtual environment
. .venv/Scripts/Activate.ps1

# Run application
python app/main.py
```

### Daily Workflow

```powershell
# Activate venv
. .venv/Scripts/Activate.ps1

# Sync with remote
git pull

# Make changes, then format/lint
ruff check --fix .
black .

# Commit (pre-commit hooks run automatically)
git add -A
git commit -m "your message"
git push
```

## Build Executable

### Standard Build

```powershell
./Build_AutoFire.ps1
```

### Debug Build (with console)

```powershell
./Build_AutoFire_Debug.ps1
```

### Cached Build (30-60x faster for unchanged code)

```powershell
./Build_AutoFire_Cached.ps1
```

Executables are generated in `dist/` directory.

## Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov=backend --cov=cad_core --cov=frontend

# Run benchmarks
pytest tests/benchmarks/

# Performance summary
pytest --benchmark-only --benchmark-autosave
```

**Current Status:** 87/89 tests passing (97.8%)

## Documentation

### For Users

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Remote Access Setup](docs/REMOTE_ACCESS_SETUP.md) - Mobile development via Android
- [Quick Start Guide](docs/REMOTE_TUNNEL_QUICKSTART.md)

### For Developers

- [Contributing Guidelines](CONTRIBUTING.md)
- [Agent Guide (HAL)](AGENTS.md)
- [API Documentation](https://obayne.github.io/AutoFireBase/) - Auto-generated via Sphinx
- [Benchmarking Guide](docs/BENCHMARKING.md)
- [Build Caching](docs/BUILD_CACHING.md)
- [Sentry Integration](docs/SENTRY_INTEGRATION.md)
- [Documentation Guide](docs/DOCUMENTATION_GUIDE.md)

### Operational Guides

- [CI/CD Pipeline](docs/ops/ci_cd.rst)
- [Performance Testing](docs/ops/benchmarking.rst)
- [Build Optimization](docs/ops/build_caching.rst)
- [Error Tracking](docs/ops/monitoring.rst)

## Project Structure

```
AutoFireBase/
├── app/           # Application entry point, dialogs, UI glue
├── frontend/      # Qt widgets, views, input handling
├── backend/       # Non-UI logic, persistence, loaders
├── cad_core/      # Geometry kernel, CAD algorithms, units
├── tests/         # pytest suite with benchmarks
├── docs/          # Sphinx documentation
├── scripts/       # Development and maintenance scripts
├── Projects/      # Sample projects and assets
└── ci/            # CI/CD configuration
```

## Code Style & Tooling

- **Formatter:** Black (line length 100)
- **Linter:** Ruff (Python 3.11 target)
- **Pre-commit:** Automatic formatting, linting, whitespace fixes
- **Testing:** pytest + pytest-benchmark + pytest-cov
- **Documentation:** Sphinx + Read the Docs theme
- **Monitoring:** Sentry SDK for error tracking

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development environment setup
- Code style guidelines
- Testing requirements
- Pull request process
- Architecture principles

**Key Principles:**

- Small, focused PRs (≤300 lines preferred)
- Keep `main` green - all work via feature branches
- Tests required for logic changes
- UI in `frontend/`, algorithms in `cad_core/`, glue in `backend/`

## Remote Development

Connect from your Android phone using VS Code Remote Tunnels:

```powershell
# One-time setup (run on development machine)
./Setup_Remote_Tunnel.ps1

# Follow prompts to authenticate and name your tunnel
# Then connect from mobile via https://vscode.dev/tunnel/<tunnel-name>
```

See [Remote Access Setup](docs/REMOTE_ACCESS_SETUP.md) for full guide.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/Obayne/AutoFireBase/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Obayne/AutoFireBase/discussions)
- **Documentation:** [https://obayne.github.io/AutoFireBase/](https://obayne.github.io/AutoFireBase/)

## Acknowledgments

Built with:

- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python
- [ezdxf](https://ezdxf.mozman.at/) - DXF import/export
- [pytest](https://docs.pytest.org/) - Testing framework
- [Sentry](https://sentry.io/) - Error tracking
- [Sphinx](https://www.sphinx-doc.org/) - Documentation generation

---

**AutoFireBase** - Professional fire protection CAD, powered by Python.
