"""Test database connection and data population."""

from db import connection

# Initialize database
connection.initialize_database(in_memory=True)
conn = connection.get_connection()
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("✓ Database tables created:")
for table in tables:
    print(f"  - {table[0]}")

print("\n📊 Checking table contents:")

# Check manufacturers
cursor.execute("SELECT COUNT(*) FROM manufacturers")
mfr_count = cursor.fetchone()[0]
print(f"  • manufacturers: {mfr_count} rows")
if mfr_count > 0:
    cursor.execute("SELECT * FROM manufacturers LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row}")

# Check device_types
cursor.execute("SELECT COUNT(*) FROM device_types")
type_count = cursor.fetchone()[0]
print(f"  • device_types: {type_count} rows")
if type_count > 0:
    cursor.execute("SELECT * FROM device_types LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row}")

# Check devices
cursor.execute("SELECT COUNT(*) FROM devices")
device_count = cursor.fetchone()[0]
print(f"  • devices: {device_count} rows")
if device_count > 0:
    cursor.execute("SELECT * FROM devices LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row}")

# Check coverage tables
cursor.execute("SELECT COUNT(*) FROM wall_strobe_coverage")
wall_count = cursor.fetchone()[0]
print(f"  • wall_strobe_coverage: {wall_count} rows")

cursor.execute("SELECT COUNT(*) FROM ceiling_strobe_coverage")
ceiling_count = cursor.fetchone()[0]
print(f"  • ceiling_strobe_coverage: {ceiling_count} rows")

cursor.execute("SELECT COUNT(*) FROM strobe_candela")
strobe_count = cursor.fetchone()[0]
print(f"  • strobe_candela: {strobe_count} rows")

print("\n🔍 Analysis:")
if mfr_count == 0 and type_count == 0 and device_count == 0:
    print("  ⚠️  ISSUE FOUND: Device catalog tables are EMPTY!")
    print("  ⚠️  The database schema exists but has NO device data")
    print("  ⚠️  User complaint 'database items missing' is VALID")
    print("\n  💡 SOLUTION NEEDED:")
    print("     - Add data population function to db/schema.py")
    print("     - Or migrate data from app/catalog.py to database")
    print("     - Or load data from JSON/CSV into database on startup")
else:
    print("  ✓ Device catalog has data")

if wall_count > 0 and ceiling_count > 0 and strobe_count > 0:
    print("  ✓ Coverage calculation tables populated correctly")
else:
    print("  ⚠️  Coverage tables missing data")
