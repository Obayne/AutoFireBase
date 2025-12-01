"""
pytest configuration for AutoFire test suite.

Ensures proper module imports by adding project root to sys.path.
"""

import sys
from pathlib import Path

# Add project root to Python path for test imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
