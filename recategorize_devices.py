import sys

sys.path.insert(0, ".")

from db import loader as db_loader


def categorize_device_better(model, manufacturer):
    """Better categorization based on user requirements."""
    model_lower = model.lower() if model else ""
    manufacturer_lower = manufacturer.lower() if manufacturer else ""

    # Fire Alarm / Life Safety systems
    fire_keywords = [
        "smoke",
        "detector",
        "sensor",
        "heat",
        "flame",
        "pull",
        "station",
        "manual",
        "horn",
        "strobe",
        "speaker",
        "bell",
        "alarm",
        "fire",
        "co",
        "carbon monoxide",
        "duct",
        "beam",
        "ionization",
        "photoelectric",
        "control panel",
        "fire alarm",
        "nac",
        "notification",
        "appliance",
        "initiating",
        "supervisory",
        "monitor",
        "relay",
        "module",
        "expander",
        "loop",
        "addressable",
        "conventional",
        "panel",
        "annunciator",
        "interface",
        "gateway",
        "slc",
        "loop card",
        "expansion",
        "power supply",
        "battery",
        "charger",
        "cabinet",
        "enclosure",
        "backbox",
    ]

    # CCTV / Surveillance systems
    cctv_keywords = [
        "camera",
        "cctv",
        "dvr",
        "nvr",
        "recorder",
        "ip camera",
        "ptz",
        "dome",
        "bullet",
        "turret",
        "lens",
        "monitor",
        "video",
        "surveillance",
        "vms",
        "encoder",
        "decoder",
        "switcher",
        "matrix",
        "multiplexer",
    ]

    # Burglar / Intrusion systems
    burg_keywords = [
        "burglar",
        "intrusion",
        "motion",
        "pir",
        "glass break",
        "shock",
        "vibration",
        "door contact",
        "window contact",
        "magnetic",
        "balance",
        "keypad",
        "reader",
        "proximity",
        "card",
        "rfid",
        "biometric",
        "fingerprint",
        "iris",
        "facial",
        "alarm panel",
        "zone",
        "partition",
        "armed",
        "disarmed",
    ]

    # Access Control systems
    access_keywords = [
        "access",
        "control",
        "lock",
        "door",
        "gate",
        "turnstile",
        "elevator",
        "intercom",
        "phone",
        "entry",
        "exit",
        "credential",
        "badge",
        "pin",
        "touchscreen",
        "reader",
        "controller",
        "panel",
        "time attendance",
        "visitor management",
        "parking",
        "lift",
        "elevator",
    ]

    # Fire alarm manufacturers - strong indicator
    fire_manufacturers = [
        "notifier",
        "simplex",
        "siemens",
        "bosch",
        "honeywell",
        "gamewell",
        "firelite",
        "autronica",
        "edwards",
        "potter",
        "hochiki",
        "mircom",
        "kidde",
        "autocall",
        "eaton wheelock",
        "system sensor",
        "monaco enterprises",
        "faraday",
        "silent knight",
    ]

    # CCTV manufacturers
    cctv_manufacturers = [
        "hikvision",
        "dahua",
        "axis",
        "hanwha",
        "bosch security",
        "pelco",
        "sony",
        "panasonic",
        "samsung",
        "ubiquiti",
        "avigilon",
        "milestone",
        "genetec",
    ]

    # Access control manufacturers
    access_manufacturers = [
        "hid",
        "lenel",
        "software house",
        "amag",
        "brivo",
        "kantech",
        "gallagher",
        "paxton",
        "dormakaba",
        "allegion",
        "salto",
        "assa abloy",
        "schlage",
    ]

    # Check manufacturer first (strongest signal)
    if any(mfg in manufacturer_lower for mfg in fire_manufacturers):
        return "Fire"
    elif any(mfg in manufacturer_lower for mfg in cctv_manufacturers):
        return "CCTV"
    elif any(mfg in manufacturer_lower for mfg in access_manufacturers):
        return "Access"

    # Check model keywords
    if any(keyword in model_lower for keyword in fire_keywords):
        return "Fire"
    elif any(keyword in model_lower for keyword in cctv_keywords):
        return "CCTV"
    elif any(keyword in model_lower for keyword in burg_keywords):
        return "Burglar"
    elif any(keyword in model_lower for keyword in access_keywords):
        return "Access"

    # Default to Fire for ambiguous devices (most common)
    return "Fire"


# Reset all type_ids first
con = db_loader.connect()
db_loader.ensure_schema(con)
cur = con.cursor()

print("Resetting device categorizations...")
cur.execute("UPDATE devices SET type_id = NULL")
con.commit()

# Get all devices and manufacturers
cur.execute(
    "SELECT d.id, d.model, d.manufacturer_id, m.name as manufacturer FROM devices d LEFT JOIN manufacturers m ON d.manufacturer_id = m.id"
)
devices = cur.fetchall()

# Get type mappings
types = {}
cur.execute("SELECT id, code FROM device_types")
for row in cur.fetchall():
    types[row["code"]] = row["id"]

print(f"Recategorizing {len(devices)} devices...")

# Categorize devices
updated = 0
for device in devices:
    device_id = device["id"]
    model = device["model"] or ""
    manufacturer = device["manufacturer"] or ""

    category = categorize_device_better(model, manufacturer)
    type_id = types.get(category)

    if type_id:
        cur.execute("UPDATE devices SET type_id = ? WHERE id = ?", (type_id, device_id))
        updated += 1

con.commit()
print(f"Updated {updated} devices")

# Show results
cur.execute(
    "SELECT dt.code, COUNT(d.id) as count FROM device_types dt LEFT JOIN devices d ON dt.id = d.type_id GROUP BY dt.code ORDER BY count DESC"
)
print("\nNew categorization:")
for row in cur.fetchall():
    print(f'  {row["code"]}: {row["count"]}')

con.close()
print("Recategorization complete!")
