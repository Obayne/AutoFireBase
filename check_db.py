import os
import sqlite3

catalog_path = os.path.join(os.path.expanduser("~"), "LV_CAD", "catalog.db")

if os.path.exists(catalog_path):
    print(f"Database found at: {catalog_path}")
    con = sqlite3.connect(catalog_path)
    cur = con.cursor()

    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cur.fetchall()
    print(f"\nTables: {[t[0] for t in tables]}")

    # Count rows in each table
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cur.fetchone()[0]
        print(f"  {table[0]}: {count} rows")

    # Sample devices if exists
    if any(t[0] == "devices" for t in tables):
        cur.execute("SELECT * FROM devices LIMIT 5")
        print("\nSample devices:")
        for row in cur.fetchall():
            print(f"  {row}")

    con.close()
else:
    print(f"Database NOT found at: {catalog_path}")
    print("Creating new database with full catalog...")
