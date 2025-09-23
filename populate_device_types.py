#!/usr/bin/env python3
"""
Script to populate device types in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def populate_device_types():
    """Populate device types in the database."""
    print("Populating device types...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Define device types
        device_types = [
            ('Detector', 'Detection devices'),
            ('Notification', 'Notification appliances'),
            ('Control', 'Control panels and units'),
            ('Initiating', 'Initiating devices'),
            ('Sensor', 'Security sensors'),
            ('Camera', 'CCTV cameras'),
            ('Recorder', 'Recording devices')
        ]
        
        # Insert device types
        for code, description in device_types:
            cur.execute("INSERT OR IGNORE INTO device_types(code, description) VALUES(?, ?)", (code, description))
            
        con.commit()
        print(f"Inserted {len(device_types)} device types")
        
        # Verify
        cur.execute("SELECT code, description FROM device_types ORDER BY code")
        types = cur.fetchall()
        print("\nDevice types in database:")
        for t in types:
            print(f"  - {t[0]}: {t[1]}")
            
        con.close()
        print("\n=== DEVICE TYPES POPULATED ===")
        
    except Exception as e:
        print(f"Error populating device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_device_types()