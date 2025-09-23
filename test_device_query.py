#!/usr/bin/env python3
"""
Script to test device querying from the AutoFire database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def test_device_query():
    """Test querying devices from the database."""
    print("Testing device queries from AutoFire database...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Query devices by manufacturer
        manufacturer = "Edwards"
        print(f"\n=== DEVICES BY MANUFACTURER: {manufacturer} ===")
        cur.execute("""
            SELECT d.name, d.symbol, dt.code as type, sc.name as category
            FROM devices d
            LEFT JOIN manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN device_types dt ON d.type_id = dt.id
            LEFT JOIN system_categories sc ON d.category_id = sc.id
            WHERE m.name = ?
            ORDER BY d.name
            LIMIT 10;
        """, (manufacturer,))
        
        devices = cur.fetchall()
        for device in devices:
            print(f"  {device[0]} [{device[1]}] - {device[2]} ({device[3]})")
            
        # Query devices by category
        category = "Smoke Detector"
        print(f"\n=== DEVICES BY CATEGORY: {category} ===")
        cur.execute("""
            SELECT d.name, m.name as manufacturer, d.symbol
            FROM devices d
            LEFT JOIN manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN system_categories sc ON d.category_id = sc.id
            WHERE sc.name = ?
            ORDER BY d.name
            LIMIT 10;
        """, (category,))
        
        devices = cur.fetchall()
        for device in devices:
            print(f"  {device[0]} by {device[1]} [{device[2]}]")
            
        # Query devices by type
        device_type = "Speaker"
        print(f"\n=== DEVICES BY TYPE: {device_type} ===")
        cur.execute("""
            SELECT d.name, m.name as manufacturer, sc.name as category
            FROM devices d
            LEFT JOIN manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN device_types dt ON d.type_id = dt.id
            LEFT JOIN system_categories sc ON d.category_id = sc.id
            WHERE dt.code = ?
            ORDER BY d.name
            LIMIT 10;
        """, (device_type,))
        
        devices = cur.fetchall()
        for device in devices:
            print(f"  {device[0]} by {device[1]} ({device[2]})")
            
        con.close()
        print("\n=== DEVICE QUERY TEST COMPLETE ===")
        
    except Exception as e:
        print(f"Error querying devices: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_device_query()