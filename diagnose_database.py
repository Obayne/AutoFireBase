#!/usr/bin/env python3
"""
Script to diagnose database issues.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def diagnose_database():
    """Diagnose database issues."""
    print("Diagnosing database...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check total device count
        cur.execute('SELECT COUNT(*) FROM devices')
        total_count = cur.fetchone()[0]
        print(f"Total devices: {total_count}")
        
        # Check categories
        cur.execute('SELECT COUNT(*) FROM system_categories')
        category_count = cur.fetchone()[0]
        print(f"Total categories: {category_count}")
        
        # Check device types
        cur.execute('SELECT COUNT(*) FROM device_types')
        type_count = cur.fetchone()[0]
        print(f"Total device types: {type_count}")
        
        # Check manufacturers
        cur.execute('SELECT COUNT(*) FROM manufacturers')
        manufacturer_count = cur.fetchone()[0]
        print(f"Total manufacturers: {manufacturer_count}")
        
        # Get sample devices
        cur.execute('SELECT * FROM devices LIMIT 5')
        devices = cur.fetchall()
        print(f"\nSample devices (first 5):")
        for device in devices:
            print(f"  {device}")
            
        # Get sample categories
        cur.execute('SELECT * FROM system_categories LIMIT 10')
        categories = cur.fetchall()
        print(f"\nSample categories (first 10):")
        for category in categories:
            print(f"  {category}")
            
        # Check if there are any fire alarm related categories
        cur.execute("SELECT * FROM system_categories WHERE name LIKE '%Fire%' OR name LIKE '%Smoke%' OR name LIKE '%Heat%' OR name LIKE '%Strobe%' OR name LIKE '%Horn%'")
        fire_categories = cur.fetchall()
        print(f"\nFire alarm related categories:")
        for category in fire_categories:
            print(f"  {category}")
            
        # Check if there are devices in these categories
        if fire_categories:
            fire_category_ids = [cat[0] for cat in fire_categories]
            placeholders = ','.join('?' * len(fire_category_ids))
            cur.execute(f"SELECT COUNT(*) FROM devices WHERE category_id IN ({placeholders})", fire_category_ids)
            fire_device_count = cur.fetchone()[0]
            print(f"\nFire alarm devices: {fire_device_count}")
            
            if fire_device_count > 0:
                cur.execute(f"SELECT d.name, sc.name as category FROM devices d JOIN system_categories sc ON d.category_id = sc.id WHERE d.category_id IN ({placeholders}) LIMIT 5", fire_category_ids)
                fire_devices = cur.fetchall()
                print(f"\nSample fire alarm devices:")
                for device in fire_devices:
                    print(f"  {device[0]} -> {device[1]}")
        
        con.close()
        
    except Exception as e:
        print(f"Error diagnosing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database()