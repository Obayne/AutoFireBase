# Minimal catalog; loads from SQLite if available, else builtin
try:
    from db import connection as db_connection
    from db import loader as db_loader
except Exception:
    db_connection = None
    db_loader = None


def _builtin():
    return [
        {
            "name": "Smoke Detector",
            "symbol": "SD",
            "type": "Detector",
            "manufacturer": "(Any)",
            "part_number": "GEN-SD",
        },
        {
            "name": "Heat Detector",
            "symbol": "HD",
            "type": "Detector",
            "manufacturer": "(Any)",
            "part_number": "GEN-HD",
        },
        {
            "name": "Strobe",
            "symbol": "S",
            "type": "Notification",
            "manufacturer": "(Any)",
            "part_number": "GEN-S",
        },
        {
            "name": "Horn Strobe",
            "symbol": "HS",
            "type": "Notification",
            "manufacturer": "(Any)",
            "part_number": "GEN-HS",
        },
        {
            "name": "Speaker",
            "symbol": "SPK",
            "type": "Notification",
            "manufacturer": "(Any)",
            "part_number": "GEN-SPK",
        },
        {
            "name": "Pull Station",
            "symbol": "PS",
            "type": "Initiating",
            "manufacturer": "(Any)",
            "part_number": "GEN-PS",
        },
    ]


def load_catalog():
    # Try to load from shared database connection first
    if db_connection is not None and db_loader is not None:
        try:
            con = db_connection.get_connection()
            devs = db_loader.fetch_devices(con)
            if devs:
                # Normalize DB results for UI safety
                return [_normalize_proto(d) for d in devs]
        except Exception:
            # If shared connection fails, fall back to separate connection
            try:
                con = db_loader.connect()
                db_loader.ensure_schema(con)
                db_loader.seed_demo(con)
                devs = db_loader.fetch_devices(con)
                con.close()
                if devs:
                    return [_normalize_proto(d) for d in devs]
            except Exception:
                pass
    return [_normalize_proto(d) for d in _builtin()]


def _normalize_proto(proto: dict) -> dict:
    """Ensure required fields exist and provide a display_name for UI.

    Rules:
    - name: string, fallback to part_number or symbol or '<unknown>'
    - type: string, fallback to 'Unknown'
    - manufacturer: string, fallback to '(Any)'
    - part_number: string, fallback to ''
    - display_name: name or part_number or symbol
    """
    if not isinstance(proto, dict):
        return proto
    p = dict(proto)  # shallow copy
    p["name"] = (p.get("name") or "").strip()
    p["part_number"] = (p.get("part_number") or "").strip()
    p["symbol"] = (p.get("symbol") or "").strip()
    if not p["name"]:
        # prefer part_number, then symbol
        p["name"] = p["part_number"] or p["symbol"] or "<unknown>"
    p["type"] = p.get("type") or "Unknown"
    p["manufacturer"] = p.get("manufacturer") or "(Any)"
    # Add a stable display_name used by UI lists
    p["display_name"] = p["name"] if p["name"] else (p["part_number"] or p["symbol"] or "<unknown>")
    return p


def list_manufacturers(devs):
    s = {"(Any)"}
    for d in devs:
        v = d.get("manufacturer", "(Any)") or "(Any)"
        s.add(v)
    return sorted(s)


def list_types(devs):
    s = {"(Any)"}
    for d in devs:
        v = d.get("type", "") or ""
        if v:
            s.add(v)
    return sorted(s)
