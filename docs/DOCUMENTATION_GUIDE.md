# Documentation Automation

AutoFire uses [Sphinx](https://www.sphinx-doc.org/) for automatic documentation generation from code docstrings.

## Quick Start

### Build Documentation Locally

**Windows:**
```powershell
cd docs
.\build.ps1 html
```

**Linux/Mac:**
```bash
cd docs
make html
```

### View Documentation

**Open in browser:**
```powershell
# Windows
Start-Process docs\_build\html\index.html

# Linux/Mac
open docs/_build/html/index.html
```

**Or serve locally:**
```powershell
cd docs
.\build.ps1 serve  # Windows
make serve         # Linux/Mac
```

Then open http://localhost:8000

## Features

### Auto-Generated API Docs

Sphinx automatically generates documentation from Python docstrings using `autodoc`:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short description.

    Longer description with more details about what this function does.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.

    Returns:
        bool: Description of return value.

    Example:
        >>> my_function("test", 42)
        True
    """
    return True
```

This appears in docs automatically!

### Supported Docstring Formats

- **Google Style** (recommended)
- **NumPy Style**
- **reStructuredText**

### Type Hints Integration

Type hints are automatically extracted and displayed:

```python
from typing import List, Optional

def process_items(items: List[str], limit: Optional[int] = None) -> int:
    """Process a list of items."""
    ...
```

Shows as: `process_items(items: List[str], limit: Optional[int] = None) → int`

## Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation page
├── build.ps1            # Windows build script
├── Makefile             # Linux/Mac build script
├── api/                 # API reference (auto-generated)
│   ├── backend.rst
│   ├── cad_core.rst
│   ├── frontend.rst
│   └── app.rst
├── ops/                 # Operational docs
│   ├── build_caching.rst
│   ├── benchmarking.rst
│   ├── monitoring.rst
│   └── ci_cd.rst
├── user/                # User guides (to be added)
├── dev/                 # Developer guides (to be added)
└── _build/              # Generated output (gitignored)
    └── html/
```

## GitHub Pages Deployment

Documentation is automatically built and deployed to GitHub Pages on every push to `main`.

### Setup (One-Time):

1. **Enable GitHub Pages**
   - Go to repository Settings → Pages
   - Source: "GitHub Actions"
   - Save

2. **Workflow runs automatically**
   - Workflow: `.github/workflows/docs.yml`
   - Builds on every push to `main`
   - Deploys to `https://<username>.github.io/<repo>/`

### View Published Docs:

After setup, docs are available at:
```
https://obayne.github.io/AutoFireBase/
```

## CI/CD Integration

Documentation builds run in CI:

```yaml
# .github/workflows/docs.yml
- name: Build documentation
  run: |
    cd docs
    sphinx-build -b html . _build/html
```

**Benefits:**
- ✅ Catch doc build errors in PRs
- ✅ Preview docs before merge
- ✅ Auto-deploy to GitHub Pages
- ✅ Free hosting

## Writing Good Documentation

### Module Docstrings

```python
"""
Brief module description.

More detailed description of the module's purpose,
what it contains, and how to use it.

Example:
    >>> from mymodule import MyClass
    >>> obj = MyClass()
"""
```

### Class Docstrings

```python
class MyClass:
    """
    Brief class description.

    Longer description explaining the class purpose,
    typical usage patterns, and important notes.

    Attributes:
        attr1 (str): Description of attribute 1.
        attr2 (int): Description of attribute 2.

    Example:
        >>> obj = MyClass("value", 42)
        >>> obj.method()
        'result'
    """
```

### Function/Method Docstrings

```python
def my_method(self, arg1: str, arg2: int = 0) -> bool:
    """
    Brief method description.

    Detailed explanation of what the method does,
    any side effects, and important behaviors.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2. Defaults to 0.

    Returns:
        bool: Description of return value.

    Raises:
        ValueError: When arg1 is empty.
        TypeError: When arg2 is negative.

    Example:
        >>> self.my_method("test", 5)
        True

    Note:
        Important note about usage or behavior.

    Warning:
        Warning about potential issues.
    """
```

## Advanced Features

### Cross-References

Reference other parts of the code:

```rst
See :func:`backend.ops_service.trim_segment` for details.
See :class:`cad_core.lines.Line` for the line class.
See :mod:`backend.models` for data models.
```

### Code Blocks

```rst
.. code-block:: python

   from app.monitoring import init_sentry
   init_sentry()
```

### Admonitions

```rst
.. note::
   This is a helpful note.

.. warning::
   This is a warning about potential issues.

.. danger::
   This is critical information.

.. tip::
   This is a useful tip.
```

### Tables

```rst
.. list-table::
   :header-rows: 1

   * - Feature
     - Status
     - Notes
   * - API Docs
     - ✅ Complete
     - Auto-generated
   * - User Guide
     - 🚧 In Progress
     - Coming soon
```

## Themes

Current theme: **Read the Docs (RTD)**

To change theme, edit `docs/conf.py`:

```python
html_theme = "sphinx_rtd_theme"  # Current
# html_theme = "alabaster"       # Default Sphinx theme
# html_theme = "pydata_sphinx_theme"  # PyData theme
```

## Troubleshooting

### "No module named 'mymodule'"

**Cause**: Sphinx can't import your code
**Fix**: Add to `docs/conf.py`:
```python
sys.path.insert(0, os.path.abspath(".."))
```

### "WARNING: document isn't included in any toctree"

**Cause**: New .rst file not added to toctree
**Fix**: Add to `index.rst` or parent .rst file:
```rst
.. toctree::
   :maxdepth: 2

   api/mymodule
```

### Build warnings/errors

**Check build output:**
```powershell
cd docs
.\build.ps1 html  # Shows all warnings/errors
```

**Common fixes:**
- Fix malformed docstrings
- Add missing type hints
- Escape special characters in docstrings

### GitHub Pages not updating

**Troubleshooting:**
1. Check Actions tab for workflow status
2. Verify Pages is enabled (Settings → Pages)
3. Check workflow file: `.github/workflows/docs.yml`
4. Wait 2-3 minutes for deployment

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
- [Google Docstring Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)

## Cost

**$0.00** - Completely free:
- Sphinx: Free, open source
- Read the Docs theme: Free
- GitHub Pages: Free hosting
- GitHub Actions: 2,000 minutes/month free
