
# app/catalog.py
# Guarantees a basic palette if no external catalog is present.

DEFAULTS = [
    {"symbol":"GEN", "name":"Generic Device", "manufacturer":"(Generic)", "part_number":"", "type":"Misc"},
    {"symbol":"SD",  "name":"Smoke Detector", "manufacturer":"(Generic)", "part_number":"SD-001", "type":"Detector"},
    {"symbol":"HD",  "name":"Heat Detector",  "manufacturer":"(Generic)", "part_number":"HD-001", "type":"Detector"},
    {"symbol":"ST",  "name":"Strobe",         "manufacturer":"(Generic)", "part_number":"ST-015", "type":"Notification"},
    {"symbol":"SP",  "name":"Speaker",        "manufacturer":"(Generic)", "part_number":"SP-015", "type":"Notification"},
]

# If you later add a JSON/CSV loader, return those; otherwise return DEFAULTS.
def load_catalog(path: str | None = None):
    try:
        if path:
            import json, os
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data
    except Exception:
        pass
    return list(DEFAULTS)

def list_manufacturers(devs):
    m = ["(Any)"]
    seen = set()
    for d in devs:
        mf = d.get("manufacturer","").strip() or "(Generic)"
        if mf not in seen:
            seen.add(mf); m.append(mf)
    return m

def list_types(devs):
    t = ["(Any)"]
    seen = set()
    for d in devs:
        ty = d.get("type","").strip() or "Misc"
        if ty not in seen:
            seen.add(ty); t.append(ty)
    return t
