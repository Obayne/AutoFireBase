"""Test that catalog loads devices from database after fix."""

from app import catalog
from db import connection

# Initialize database (as main.py does)
connection.initialize_database(in_memory=True)

# Load catalog (should now use shared connection)
devices = catalog.load_catalog()

print(f"✓ Catalog loaded {len(devices)} devices")
print("\n📋 Devices from catalog:")
for device in devices:
    print(f"  • {device['name']} ({device['type']}) - {device['manufacturer']}")

# Verify they came from database
conn = connection.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM devices")
db_count = cursor.fetchone()[0]

print(f"\n✓ Database has {db_count} device records")

if len(devices) == db_count and db_count > 0:
    print("\n✅ SUCCESS: Catalog is now loading from shared database!")
    print("✅ Database connectivity issue FIXED")
else:
    print(f"\n⚠️  Mismatch: Catalog has {len(devices)} but DB has {db_count}")
