"""Pytest conftest for smoke tests.

Ensure the repository root is on sys.path so newly added top-level packages
like `lv_cad` are discoverable during test runs in CI and locally.
"""

import sys
from pathlib import Path

# Insert project root (two levels up from tests/) at the front of sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
