import os
import sqlite3

for db_file in ["autofire.db", "backup.db"]:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            print(f"{db_file} tables: {[t[0] for t in tables]}")

            # Check if there's a devices table
            if any("device" in t[0].lower() for t in tables):
                for table_name in [t[0] for t in tables if "device" in t[0].lower()]:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"{db_file} {table_name}: {count} records")

            conn.close()
        except Exception as e:
            print(f"Error reading {db_file}: {e}")
