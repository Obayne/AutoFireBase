#!/usr/bin/env python3
"""
Explore database structure for panels and expansion boards.
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(__file__))


def explore_panel_tables():
    """Explore panel-related tables in the database."""
    print("Exploring panel database structure...")

    conn = sqlite3.connect("autofire.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]

    # Find panel-related tables
    panel_tables = [table for table in all_tables if "panel" in table.lower()]
    print(f"\nPanel-related tables: {panel_tables}")

    # Examine specific tables
    for table in panel_tables:
        print(f"\n--- Table: {table} ---")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['name']}: {col['type']}")

        # Show sample data
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")

        if count > 0 and count < 10:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            samples = cursor.fetchall()
            for i, sample in enumerate(samples):
                print(f"  Sample {i+1}: {dict(sample)}")

    # Look for expansion board related data
    print("\n--- Looking for expansion boards ---")
    cursor.execute(
        "SELECT * FROM devices WHERE name LIKE '%expansion%' OR name LIKE '%board%' "
        "OR name LIKE '%module%' LIMIT 10"
    )
    expansion_devices = cursor.fetchall()
    for device in expansion_devices:
        print(f"  {device['name']} ({device['manufacturer']}) - {device['symbol']}")

    conn.close()


if __name__ == "__main__":
    explore_panel_tables()
