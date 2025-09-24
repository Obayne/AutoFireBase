from __future__ import annotations

CURRENT_VERSION = "0.1.0"


def get_version() -> str:
    return CURRENT_VERSION


def is_compatible(ver: str) -> bool:
    """
    Compatibility policy: match by major version.
    Versions with the same major number are considered compatible.
    """
    try:
        major_current = CURRENT_VERSION.split(".")[0]
        major_input = ver.split(".")[0]
        return major_current == major_input
    except Exception:
        return False
