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
        # NFPA 170 Fire Safety Symbols
        {
            "name": "Exit Sign",
            "symbol": "EXIT",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-EXIT",
        },
        {
            "name": "Directional Arrow Right",
            "symbol": "\u2192",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-ARROW-R",
        },
        {
            "name": "Directional Arrow Left",
            "symbol": "\u2190",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-ARROW-L",
        },
        {
            "name": "Directional Arrow Up",
            "symbol": "\u2191",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-ARROW-U",
        },
        {
            "name": "Directional Arrow Down",
            "symbol": "\u2193",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-ARROW-D",
        },
        {
            "name": "Fire Extinguisher",
            "symbol": "EXT",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-EXT",
        },
        {
            "name": "Fire Hose",
            "symbol": "HOSE",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-HOSE",
        },
        {
            "name": "Fire Alarm",
            "symbol": "ALARM",
            "type": "NFPA 170",
            "manufacturer": "(Any)",
            "part_number": "NFPA-ALARM",
        },
    ]


def load_catalog():
    if db_connection is not None and db_loader is not None:
        try:
            # Use the main app's database connection
            db_connection.initialize_database(in_memory=False)
            con = db_connection.get_connection()
            db_loader.ensure_schema(con)
            # Don't seed demo here - the main app handles seeding
            devs = db_loader.fetch_devices(con)
            if devs:
                # Normalize DB results for UI safety
                return [_normalize_proto(d) for d in devs]
        except Exception as e:
            print(f"Error loading catalog from main DB: {e}")

    # Fallback to demo catalog
    return [_normalize_proto(d) for d in _builtin()]


def _normalize_proto(proto: dict) -> dict:
    """Ensure required fields exist and provide a display_name for UI.

    Rules:
    - name: string, fallback to model/part_number or symbol or '<unknown>'
    - type: string, fallback to 'Unknown'
    - manufacturer: string, fallback to '(Any)'
    - part_number: string, fallback to model or ''
    - display_name: name or part_number or symbol
    """
    if not isinstance(proto, dict):
        return proto
    p = dict(proto)  # shallow copy
    p["name"] = (p.get("name") or "").strip()
    p["part_number"] = (p.get("part_number") or p.get("model") or "").strip()
    p["symbol"] = (p.get("symbol") or "").strip()
    if not p["name"]:
        # For database devices, prefer model, then part_number, then symbol
        p["name"] = p.get("model") or p["part_number"] or p["symbol"] or "<unknown>"
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


def get_device_types():
    """Get all available device types without loading full catalog."""
    try:
        if db_loader is not None:
            con = db_loader.connect()
            db_loader.ensure_schema(con)
            types = db_loader.get_device_types(con)
            con.close()
            if types:
                return set(types)
    except Exception:
        pass

    # Fallback to builtin types
    return set(d.get("type", "Unknown") for d in _builtin())


def get_devices_by_type(device_type):
    """Get devices of a specific type."""
    try:
        if db_loader is not None:
            con = db_loader.connect()
            db_loader.ensure_schema(con)
            devices = db_loader.get_devices_by_type(con, device_type)
            con.close()
            if devices:
                return [_normalize_proto(d) for d in devices]
    except Exception:
        pass


def search_devices(search_text="", device_type="", manufacturer=""):
    """Search devices by text, type, and manufacturer."""
    try:
        if db_loader is not None:
            con = db_loader.connect()
            db_loader.ensure_schema(con)
            devices = db_loader.search_devices(con, search_text, device_type, manufacturer)
            con.close()
            if devices:
                return [_normalize_proto(d) for d in devices]
    except Exception:
        pass

    # Fallback to filtering builtin devices
    devices = _builtin()
    if device_type:
        devices = [d for d in devices if d.get("type") == device_type]
    if manufacturer:
        devices = [d for d in devices if d.get("manufacturer") == manufacturer]

    if search_text:
        search_lower = search_text.lower()
        devices = [
            d
            for d in devices
            if (
                search_lower in d.get("name", "").lower()
                or search_lower in d.get("manufacturer", "").lower()
                or search_lower in d.get("part_number", "").lower()
            )
        ]

    return [_normalize_proto(d) for d in devices]
