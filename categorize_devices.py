import sys

sys.path.insert(0, ".")

from db import loader as db_loader


def categorize_device(model, manufacturer):
    """Categorize a device based on its model and manufacturer."""
    model_lower = model.lower()
    manufacturer_lower = manufacturer.lower() if manufacturer else ""

    # Fire Alarm / Detection devices
    fire_keywords = [
        "smoke",
        "detector",
        "sensor",
        "heat",
        "flame",
        "pull",
        "station",
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
    ]

    # CCTV / Camera devices
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
    ]

    # Burglar / Intrusion devices
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
    ]

    # Access Control devices
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
    ]

    # Check for fire alarm devices
    if any(keyword in model_lower for keyword in fire_keywords):
        return "Detector"  # Most fire devices are detectors/sensors

    # Check for CCTV
    if any(keyword in model_lower for keyword in cctv_keywords):
        return "Camera"

    # Check for burglar
    if any(keyword in model_lower for keyword in burg_keywords):
        return "Sensor"

    # Check for access control
    if any(keyword in model_lower for keyword in access_keywords):
        return "Control"

    # Default to Detector for fire alarm manufacturers
    fire_manufacturers = [
        "notifier",
        "simplex",
        "siemens",
        "bosch",
        "honeywell",
        "gamewell",
        "firelite",
        "autronica",
    ]
    if any(mfg in manufacturer_lower for mfg in fire_manufacturers):
        return "Detector"

    # Default to Control for other devices
    return "Control"


# Main categorization script
con = db_loader.connect()
db_loader.ensure_schema(con)
cur = con.cursor()

print("Starting device categorization...")

# Get all devices
cur.execute("SELECT id, model, manufacturer_id FROM devices")
devices = cur.fetchall()

# Get manufacturer names
manufacturers = {}
cur.execute("SELECT id, name FROM manufacturers")
for row in cur.fetchall():
    manufacturers[row["id"]] = row["name"]

# Get existing type mappings
types = {}
cur.execute("SELECT id, code FROM device_types")
for row in cur.fetchall():
    types[row["code"]] = row["id"]

print(f"Found {len(devices)} devices to categorize")
print(f"Available types: {list(types.keys())}")

# Categorize and update
updated = 0
for device in devices:
    device_id = device["id"]
    model = device["model"] or ""
    manufacturer = manufacturers.get(device["manufacturer_id"], "")

    category = categorize_device(model, manufacturer)
    type_id = types.get(category)

    if type_id:
        cur.execute("UPDATE devices SET type_id = ? WHERE id = ?", (type_id, device_id))
        updated += 1
        if updated % 1000 == 0:
            print(f"Updated {updated} devices...")

con.commit()
print(f"Updated {updated} devices with type assignments")

# Verify the results
cur.execute(
    "SELECT dt.code, COUNT(d.id) as count FROM device_types dt LEFT JOIN devices d ON dt.id = d.type_id GROUP BY dt.code ORDER BY count DESC"
)
print("\nFinal categorization:")
for row in cur.fetchall():
    print(f'  {row["code"]}: {row["count"]}')

con.close()
print("Categorization complete!")
