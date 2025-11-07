"""
Branding and version information (migrated to lv_cad.backend).
"""

import os
from pathlib import Path

# Product branding
PRODUCT_NAME = "LV CAD"
APP_NAME = "LV_CAD"


# Version information
def get_version():
    """Get the current version from VERSION.txt or return default."""
    version_file = Path(__file__).parent.parent / "VERSION.txt"
    try:
        with open(version_file) as f:
            return f.read().strip()
    except Exception:
        return "1.0.0-dev"


# Company information
COMPANY_NAME = "Low Voltage CAD Systems"
COMPANY_URL = "https://github.com/Obayne/AutoFireBase"


# Application paths
def get_app_data_dir():
    """Get the application data directory."""
    if os.name == "nt":  # Windows
        base_dir = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    else:  # Linux/Mac
        base_dir = str(Path.home() / ".config")

    return Path(base_dir) / COMPANY_NAME / APP_NAME


def get_log_dir():
    """Get the log directory."""
    return get_app_data_dir() / "logs"
