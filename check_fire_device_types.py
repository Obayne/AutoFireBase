#!/usr/bin/env python3
"""
Script to check fire-related device types in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_fire_device_types():
    """Check fire-related device types in the database."""
    print("Checking fire-related device types...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Get fire-related device types
        cur.execute("""
            SELECT DISTINCT dt.code 
            FROM device_types dt 
            JOIN devices d ON dt.id = d.type_id 
            WHERE dt.code LIKE '%Detector%' OR dt.code LIKE '%Notification%' OR dt.code LIKE '%Control%' OR dt.code LIKE '%Initiating%'
            ORDER BY dt.code
        """)
        
        types = cur.fetchall()
        print("Fire-related device types:")
        for t in types:
            print(f"  - {t[0]}")
            
        # Get count of devices for each type
        print("\nDevice counts by type:")
        for t in types:
            cur.execute("""
                SELECT COUNT(*) 
                FROM devices d 
                JOIN device_types dt ON d.type_id = dt.id 
                WHERE dt.code = ?
            """, (t[0],))
            
            count = cur.fetchone()[0]
            print(f"  - {t[0]}: {count} devices")
            
        con.close()
        
    except Exception as e:
        print(f"Error checking fire device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_fire_device_types()