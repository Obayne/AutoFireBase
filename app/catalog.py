# Minimal catalog; loads from SQLite if available, else builtin
import os
try:
    from db import loader as db_loader
except Exception:
    db_loader = None

def _builtin():
    return [
        # Fire Alarm Devices
        {"name":"Smoke Detector", "symbol":"SD", "type":"Detector", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-SD"},
        {"name":"Heat Detector",  "symbol":"HD", "type":"Detector", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-HD"},
        {"name":"Strobe",         "symbol":"S",  "type":"Notification", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-S"},
        {"name":"Horn Strobe",    "symbol":"HS", "type":"Notification", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-HS"},
        {"name":"Speaker",        "symbol":"SPK","type":"Notification", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-SPK"},
        {"name":"Pull Station",   "symbol":"PS", "type":"Initiating", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-PS"},
        # Fire Alarm Control Panels
        {"name":"FACP Panel",     "symbol":"FACP","type":"Control", "system_category":"Fire Alarm", "manufacturer":"(Any)", "part_number":"GEN-FACP"},
        # Security Devices
        {"name":"Motion Detector", "symbol":"MD", "type":"Sensor", "system_category":"Security", "manufacturer":"(Any)", "part_number":"GEN-MD"},
        {"name":"Door Contact",    "symbol":"DC", "type":"Sensor", "system_category":"Security", "manufacturer":"(Any)", "part_number":"GEN-DC"},
        # CCTV Devices
        {"name":"Camera",          "symbol":"CAM", "type":"Camera", "system_category":"CCTV", "manufacturer":"(Any)", "part_number":"GEN-CAM"},
        {"name":"DVR",             "symbol":"DVR", "type":"Recorder", "system_category":"CCTV", "manufacturer":"(Any)", "part_number":"GEN-DVR"},
    ]

def load_catalog():
    if db_loader is not None:
        try:
            con = db_loader.connect()
            db_loader.ensure_schema(con)
            db_loader.seed_demo(con)
            devs = db_loader.fetch_devices(con)
            con.close()
            if devs:
                return devs
        except Exception:
            pass
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