# Minimal, built-in catalog with filters; replace with DB later
def _builtin():
    return [
        {"name":"Smoke Detector", "symbol":"SD", "type":"Detector", "manufacturer":"(Any)", "part_number":"GEN-SD"},
        {"name":"Heat Detector",  "symbol":"HD", "type":"Detector", "manufacturer":"(Any)", "part_number":"GEN-HD"},
        {"name":"Strobe",         "symbol":"S",  "type":"Notification", "manufacturer":"(Any)", "part_number":"GEN-S"},
        {"name":"Horn Strobe",    "symbol":"HS", "type":"Notification", "manufacturer":"(Any)", "part_number":"GEN-HS"},
        {"name":"Speaker",        "symbol":"SPK","type":"Notification", "manufacturer":"(Any)", "part_number":"GEN-SPK"},
        {"name":"Pull Station",   "symbol":"PS", "type":"Initiating", "manufacturer":"(Any)", "part_number":"GEN-PS"},
    ]

def load_catalog():
    # In the future, look for a JSON file; for now return builtin
    return _builtin()

def list_manufacturers(devs):
    s = {"(Any)"}
    for d in devs:
        v = d.get("manufacturer","(Any)") or "(Any)"
        s.add(v)
    return sorted(s)

def list_types(devs):
    s = {"(Any)"}
    for d in devs:
        v = d.get("type","") or ""
        if v: s.add(v)
    return sorted(s)
