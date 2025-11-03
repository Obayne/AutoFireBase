#!/usr/bin/env python3
"""Test script to verify wire spool is working."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3


def test_wire_spool_data():
    """Test that wires can be loaded from database."""
    print("Testing wire spool database loading...")

    try:
        con = sqlite3.connect("autofire.db")
        cur = con.cursor()

        # Same query as used in the app
        cur.execute(
            """
            SELECT w.name, w.gauge, w.color, wt.code AS type,
                   w.ohms_per_1000ft, w.max_current_a, w.model
            FROM wires w
            LEFT JOIN wire_types wt ON w.type_id = wt.id
            ORDER BY w.gauge, w.name
        """
        )

        wires = cur.fetchall()
        con.close()

        print(f"Found {len(wires)} wires in database:")
        for wire in wires:
            name, gauge, color, wire_type, ohms, max_current, model = wire

            # Create display name like in the app
            if wire_type:
                display_name = f"{gauge} AWG {wire_type} - {color}"
            else:
                display_name = f"{gauge} AWG - {color}"

            specs = f"({ohms:.1f} Ω/1000ft, {max_current:.0f}A)"
            full_display = f"{display_name} {specs}"

            print(f"  • {full_display}")

        return len(wires) > 0

    except Exception as e:
        print(f"Error loading wires: {e}")
        return False


if __name__ == "__main__":
    print("=== Wire Spool Test ===")
    success = test_wire_spool_data()
    print(f"\nResult: {'✅ PASS' if success else '❌ FAIL'}")
    print("\nIf this passes, the wire spool should be populated in the app.")
    print("Check the 'Wire Spool' tab in the left dock panel.")
