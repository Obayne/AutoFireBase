"""Root conftest.py to ensure package modules are importable during testing."""

import sys
from pathlib import Path

# Add the repository root to sys.path so that frontend, backend, etc. can be imported
repo_root = Path(__file__).parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))
