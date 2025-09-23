#!/usr/bin/env python3
"""
Simple diagnostic script to understand the database structure.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def simple_diagnostic():
    """Simple diagnostic to understand the database structure."""
    print("Running simple diagnostic...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check total device count
        cur.execute('SELECT COUNT(*) FROM devices')
        total_count = cur.fetchone()[0]
        print(f"Total devices: {total_count}")
        
        # Get a few sample devices with their categories
        cur.execute('''
            SELECT d.id, d.name, sc.name as category 
            FROM devices d 
            JOIN system_categories sc ON d.category_id = sc.id 
            LIMIT 10
        ''')
        sample_devices = cur.fetchall()
        print("\nSample devices with categories:")
        for device in sample_devices:
            print(f"  ID: {device[0]}, Name: {device[1]}, Category: {device[2]}")
            
        # Try a simple query to find fire alarm devices
        cur.execute('''
            SELECT COUNT(*) 
            FROM devices d 
            JOIN system_categories sc ON d.category_id = sc.id 
            WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Smoke%' OR sc.name LIKE '%Heat%'
        ''')
        fire_count = cur.fetchone()[0]
        print(f"\nDevices with Fire/Smoke/Heat in category name: {fire_count}")
        
        # Get some fire alarm devices
        if fire_count > 0:
            cur.execute('''
                SELECT d.id, d.name, sc.name as category 
                FROM devices d 
                JOIN system_categories sc ON d.category_id = sc.id 
                WHERE sc.name LIKE '%Fire%' OR sc.name LIKE '%Smoke%' OR sc.name LIKE '%Heat%'
                LIMIT 5
            ''')
            fire_devices = cur.fetchall()
            print("\nSample fire alarm devices:")
            for device in fire_devices:
                print(f"  ID: {device[0]}, Name: {device[1]}, Category: {device[2]}")
        
        con.close()
        
    except Exception as e:
        print(f"Error in diagnostic: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_diagnostic()