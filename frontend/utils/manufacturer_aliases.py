"""
Utility for normalizing manufacturer names to canonical brands for UI filtering and display.
"""

CANONICALS = [
    ("fire", "lite", "Fire-Lite Alarms"),
    ("notifier", None, "NOTIFIER"),
    ("gamewell", None, "Gamewell-FCI"),
    ("silent", "knight", "Silent Knight"),
    ("system sensor", None, "System Sensor"),
    ("vesda", None, "Xtralis/VESDA"),
    ("xtralis", None, "Xtralis/VESDA"),
]


def normalize_manufacturer(name):
    if not isinstance(name, str):
        return name
    low = name.lower().replace(" ", "").replace(">", "")
    for a, b, canon in CANONICALS:
        if a in low and (b is None or b in low):
            return canon
    return name.strip()
