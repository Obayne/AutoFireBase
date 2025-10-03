import os
import sqlite3

# Check if database exists
if os.path.exists("autofire.db"):
    conn = sqlite3.connect("autofire.db")
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Database tables:", [t[0] for t in tables])

    # Check for wire-related tables
    for table in tables:
        table_name = table[0]
        if "wire" in table_name.lower():
            print(f"\n{table_name} table:")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("Columns:", [col[1] for col in columns])

            # Show some sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            rows = cursor.fetchall()
            print(f"Sample data ({len(rows)} rows):")
            for row in rows:
                print(" ", row)

    conn.close()
else:
    print("Database not found")
