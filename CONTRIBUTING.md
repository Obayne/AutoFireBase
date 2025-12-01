# Contributing to AutoFireBase

Thank you for your interest in contributing to AutoFireBase! This guide will help you get started with development, understand our workflow, and make quality contributions.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Code Style](#code-style)
- [Architecture Principles](#architecture-principles)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [DevOps Workflows](#devops-workflows)
- [Communication](#communication)

## Getting Started

### Prerequisites

- **Python 3.11** (recommended, 3.10+ supported)
- **Git** for version control
- **PowerShell** (Windows) or Bash (Linux/Mac)
- **VS Code** (recommended) with Python extension

### First-Time Setup

1. **Fork and Clone**

   ```powershell
   git clone https://github.com/YOUR_USERNAME/AutoFireBase.git
   cd AutoFireBase
   ```

2. **Run Automated Setup**

   ```powershell
   ./setup_dev.ps1  # Windows
   # or
   ./setup_dev.sh   # Linux/Mac (if available)
   ```

   This script:
   - Creates a Python virtual environment (`.venv`)
   - Installs all dependencies from `requirements.txt` and `requirements-dev.txt`
   - Sets up pre-commit hooks for automatic formatting and linting
   - Validates the installation

3. **Activate Virtual Environment**

   ```powershell
   # Windows PowerShell
   . .venv/Scripts/Activate.ps1

   # Linux/Mac
   source .venv/bin/activate
   ```

4. **Verify Installation**

   ```powershell
   # Run test suite
   pytest

   # Run application
   python app/main.py
   ```

## Development Environment

### Recommended VS Code Extensions

- **Python** (ms-python.python) - Python language support
- **Pylance** (ms-python.vscode-pylance) - Fast Python language server
- **Black Formatter** (ms-python.black-formatter) - Code formatting
- **Ruff** (charliermarsh.ruff) - Fast Python linter
- **GitLens** (eamodio.gitlens) - Enhanced Git integration
- **Error Lens** (usernamehw.errorlens) - Inline error display

### Project Structure

```
AutoFireBase/
├── app/           # Application entry point, dialogs, UI glue
│   ├── main.py    # Primary entry point
│   ├── dialogs/   # UI dialogs
│   ├── tools/     # Tool implementations
│   └── ui/        # UI components
├── frontend/      # Qt widgets, views, input handling
│   ├── app.py     # Alternative entry point
│   ├── qt_shapes.py
│   └── tool_registry.py
├── backend/       # Non-UI logic, persistence, loaders
│   ├── models.py
│   ├── catalog_store.py
│   └── coverage_service.py
├── cad_core/      # Geometry kernel, CAD algorithms, units
│   ├── lines.py
│   ├── circle.py
│   ├── arc.py
│   └── fillet.py
├── tests/         # pytest suite with benchmarks
│   ├── benchmarks/
│   ├── cad_core/
│   ├── backend/
│   └── frontend/
├── docs/          # Sphinx documentation
└── scripts/       # Development and maintenance scripts
```

### Architecture Principles

**Separation of Concerns:**

- **Frontend:** Qt widgets, views, user input handling, rendering
- **Backend:** Business logic, data persistence, file I/O, services
- **CAD Core:** Pure geometry algorithms, no Qt dependencies
- **App:** Glue layer connecting frontend, backend, and core

**Key Rules:**

1. **No GUI in `cad_core/`** - Keep geometry algorithms pure
2. **No Qt in `backend/`** - Business logic must be testable without GUI
3. **Prefer composition** over large monolithic classes
4. **Avoid module-level side effects** - Use explicit initialization
5. **Small, focused modules** - Each file should have a single responsibility

## Code Style

### Formatting

We use **Black** with a line length of 100 characters:

```powershell
# Format all files
black .

# Format specific file
black app/main.py
```

Configuration in `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Linting

We use **Ruff** for fast linting and import sorting:

```powershell
# Check all files
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific file
ruff check app/main.py
```

Configuration in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W"]
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

- **Ruff** - Linting and import sorting
- **Black** - Code formatting
- **Trailing whitespace** - Removes trailing spaces
- **End of file** - Ensures newline at EOF
- **Secrets detection** - Prevents committing API keys

To run manually:

```powershell
pre-commit run --all-files
```

### Import Style

Use absolute imports from project root:

```python
# Good
from app.dialogs.device_props import DevicePropertiesDialog
from cad_core.lines import intersection_line_line
from backend.models import Device

# Avoid
from .dialogs.device_props import DevicePropertiesDialog  # relative
from lines import intersection_line_line  # ambiguous
```

### Docstrings

Use Google-style docstrings for Sphinx documentation:

```python
def extend_line_to_intersection(
    line: Line, other: Line, end: str = "b", tol: float = 1e-9
) -> Line | None:
    """Extend one end of 'line' to meet the infinite intersection with 'other'.

    Args:
        line: The line to extend
        other: The line to intersect with
        end: Which end to extend ('a' or 'b')
        tol: Numerical tolerance for intersection detection

    Returns:
        New Line with extended endpoint, or None if lines are parallel

    Raises:
        ValueError: If end is not 'a' or 'b'
    """
```

## Testing Requirements

### Test Coverage

All logic changes **must** include tests. Aim for:

- **80%+ coverage** for new code
- **100% coverage** for critical geometry algorithms
- **Integration tests** for UI workflows (where practical)

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov=backend --cov=cad_core --cov=frontend

# Run specific test file
pytest tests/cad_core/test_lines.py

# Run specific test
pytest tests/cad_core/test_lines.py::test_intersection_line_line

# Run benchmarks
pytest tests/benchmarks/ --benchmark-only

# Run with verbose output
pytest -v
```

### Writing Tests

#### Unit Tests (cad_core, backend)

```python
# tests/cad_core/test_lines.py
import pytest
from cad_core.lines import Line, Point, intersection_line_line

def test_intersection_line_line_perpendicular():
    """Test intersection of two perpendicular lines."""
    l1 = Line(Point(0, 0), Point(2, 0))
    l2 = Line(Point(1, -1), Point(1, 1))

    result = intersection_line_line(l1, l2)

    assert result is not None
    assert abs(result.x - 1.0) < 1e-9
    assert abs(result.y - 0.0) < 1e-9

def test_intersection_line_line_parallel():
    """Test that parallel lines return None."""
    l1 = Line(Point(0, 0), Point(2, 0))
    l2 = Line(Point(0, 1), Point(2, 1))

    result = intersection_line_line(l1, l2)

    assert result is None
```

#### Benchmark Tests

```python
# tests/benchmarks/test_bench_lines.py
import pytest
from cad_core.lines import Line, Point, intersection_line_line

@pytest.fixture
def perpendicular_lines():
    """Fixture for perpendicular line pair."""
    return (
        Line(Point(0, 0), Point(10, 0)),
        Line(Point(5, -5), Point(5, 5))
    )

def test_bench_intersection_line_line(benchmark, perpendicular_lines):
    """Benchmark line-line intersection."""
    l1, l2 = perpendicular_lines
    result = benchmark(intersection_line_line, l1, l2)
    assert result is not None
```

### Test Organization

```
tests/
├── benchmarks/           # Performance benchmarks
│   ├── test_bench_lines.py
│   └── test_bench_circles.py
├── cad_core/             # Pure geometry tests
│   ├── test_lines.py
│   ├── test_circle.py
│   └── test_fillet.py
├── backend/              # Business logic tests
│   ├── test_models.py
│   └── test_coverage_service.py
├── frontend/             # UI tests (minimal GUI)
│   └── test_tool_registry.py
└── conftest.py           # Shared fixtures
```

## Pull Request Process

### 1. Create Feature Branch

Use descriptive branch names:

```powershell
# Features
git checkout -b feat/circle-fillet-tool

# Bug fixes
git checkout -b fix/dxf-import-crash

# Chores/maintenance
git checkout -b chore/update-dependencies
```

### 2. Make Focused Changes

**Keep PRs small and focused:**

- Prefer **≤300 lines** per PR
- One logical change per PR
- Separate refactoring from feature work
- Split large features into multiple PRs

### 3. Write Clear Commit Messages

```
<type>: <short summary> (50 chars max)

<detailed explanation if needed>
<wrap at 72 characters>

- Bullet points OK for lists
- Reference issues: Fixes #123
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`

Examples:

```
feat: Add circle-circle fillet tool

Implements geometric algorithm for filleting two circles with
a specified radius. Supports internal and external tangents.

- Added fillet_circles() to cad_core/fillet.py
- Added CircleFilletTool to app/tools/
- Added 8 unit tests with edge cases

Refs #45
```

### 4. Ensure Tests Pass

Before pushing:

```powershell
# Format and lint
ruff check --fix .
black .

# Run full test suite
pytest

# Check coverage
pytest --cov=app --cov=backend --cov=cad_core
```

### 5. Push and Create PR

```powershell
git push -u origin feat/circle-fillet-tool
```

Then create PR on GitHub with:

- **Clear title** describing the change
- **Description** explaining what/why/how
- **Screenshots** for UI changes
- **Related issues** (Fixes #123, Closes #456)
- **Testing notes** for reviewers

### 6. Code Review

- Address reviewer feedback promptly
- Keep discussions respectful and constructive
- Make requested changes in new commits (don't force-push during review)
- Squash commits before final merge if requested

### 7. Merge

Once approved:

- Ensure CI passes (all checks green)
- Squash merge (preferred for clean history)
- Delete feature branch after merge

## DevOps Workflows

### Performance Testing

**When to benchmark:**

- Adding new geometry algorithms
- Optimizing existing algorithms
- Before/after performance improvements

```powershell
# Run benchmarks
pytest tests/benchmarks/ --benchmark-only

# Compare with baseline
pytest tests/benchmarks/ --benchmark-compare=0001

# Save baseline
pytest tests/benchmarks/ --benchmark-autosave
```

**Performance targets:**

- Line-line intersection: **< 5µs**
- Circle-line intersection: **< 10µs**
- Fillet operations: **< 20µs**

See [Benchmarking Guide](docs/BENCHMARKING.md) for details.

### Build Caching

Use cached builds for faster iteration:

```powershell
# First build (slow)
./Build_AutoFire_Cached.ps1

# Subsequent builds (30-60x faster if no changes)
./Build_AutoFire_Cached.ps1
```

See [Build Caching](docs/BUILD_CACHING.md) for details.

### Error Tracking

Sentry integration for production error tracking:

```python
from app.monitoring import capture_exception, add_breadcrumb

try:
    # Risky operation
    result = complex_calculation()
except Exception as e:
    capture_exception(e)
    raise
```

See [Sentry Integration](docs/SENTRY_INTEGRATION.md) for setup.

### Documentation

Build and preview docs locally:

```powershell
cd docs
./build.ps1 html  # Windows
make html         # Linux/Mac

# Serve locally
./build.ps1 serve  # Opens http://localhost:8000
```

Documentation auto-deploys to GitHub Pages on merge to `main`.

See [Documentation Guide](docs/DOCUMENTATION_GUIDE.md) for details.

## Communication

### GitHub Issues

**Before creating an issue:**

1. Search existing issues to avoid duplicates
2. Use issue templates when available
3. Provide clear, minimal reproduction steps
4. Include environment details (OS, Python version)

**Issue labels:**

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

### GitHub Discussions

Use Discussions for:

- Questions about usage or development
- Feature proposals and design discussions
- Showcasing projects built with AutoFireBase

### Pull Request Reviews

**As author:**

- Respond to all review comments
- Mark conversations as resolved when addressed
- Request re-review when ready

**As reviewer:**

- Be constructive and respectful
- Suggest specific improvements
- Approve when ready, request changes if needed

## Additional Resources

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Agent Guide (HAL)](AGENTS.md)
- [API Documentation](https://obayne.github.io/AutoFireBase/)
- [Benchmarking Guide](docs/BENCHMARKING.md)
- [Build Caching](docs/BUILD_CACHING.md)
- [Sentry Integration](docs/SENTRY_INTEGRATION.md)

## License

By contributing to AutoFireBase, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AutoFireBase! 🔥
