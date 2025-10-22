#!/usr/bin/env python3
"""
Query expansion boards and modules from database.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from db.connection import get_connection, initialize_database


def query_expansion_boards():
    """Query expansion boards from database."""
    initialize_database(in_memory=False)
    con = get_connection()
    cur = con.cursor()

    # Query for expansion boards and modules
    cur.execute(
        """
        SELECT name, manufacturer, symbol, type
        FROM devices
        WHERE name LIKE '%expansion%'
           OR name LIKE '%board%'
           OR name LIKE '%module%'
           OR type = 'Panel'
        LIMIT 20
    """
    )

    results = cur.fetchall()
    print(f"Found {len(results)} expansion boards/modules:")
    for row in results:
        print(f"  {row[0]} ({row[1]}) - {row[2]} [{row[3]}]")

    # Also check panel types
    cur.execute("SELECT DISTINCT type FROM devices ORDER BY type")
    types = [row[0] for row in cur.fetchall()]
    print(f"\nDevice types: {types}")


if __name__ == "__main__":
    query_expansion_boards()
