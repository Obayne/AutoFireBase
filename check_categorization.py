import sys

sys.path.insert(0, ".")
from db import loader as db_loader

con = db_loader.connect()
db_loader.ensure_schema(con)
cur = con.cursor()

# Check current categorization
cur.execute(
    "SELECT dt.code, COUNT(d.id) as count FROM device_types dt LEFT JOIN devices d ON dt.id = d.type_id GROUP BY dt.code ORDER BY count DESC"
)
print("Current categorization:")
for row in cur.fetchall():
    print(f'  {row["code"]}: {row["count"]}')

# Check some examples from each major category
print("\nDetector examples:")
cur.execute(
    'SELECT d.model, m.name FROM devices d JOIN manufacturers m ON d.manufacturer_id = m.id WHERE d.type_id = (SELECT id FROM device_types WHERE code = "Detector") LIMIT 5'
)
for row in cur.fetchall():
    print(f'  {row["name"]}: {row["model"]}')

print("\nControl examples:")
cur.execute(
    'SELECT d.model, m.name FROM devices d JOIN manufacturers m ON d.manufacturer_id = m.id WHERE d.type_id = (SELECT id FROM device_types WHERE code = "Control") LIMIT 5'
)
for row in cur.fetchall():
    print(f'  {row["name"]}: {row["model"]}')

# Check manufacturers
cur.execute(
    "SELECT m.name, COUNT(d.id) as count FROM manufacturers m LEFT JOIN devices d ON m.id = d.manufacturer_id GROUP BY m.name ORDER BY count DESC LIMIT 10"
)
print("\nTop manufacturers:")
for row in cur.fetchall():
    print(f'  {row["name"]}: {row["count"]}')

con.close()
