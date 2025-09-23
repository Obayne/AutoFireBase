#!/usr/bin/env python3
"""
Script to check device types in the database.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.loader import connect

def check_device_types():
    """Check device types in the database."""
    print("Checking device types...")
    
    try:
        con = connect()
        cur = con.cursor()
        
        # Check device types
        cur.execute('SELECT * FROM device_types')
        types = cur.fetchall()
        print(f"Device types ({len(types)}):")
        for t in types:
            print(f"  {t}")
            
        # Check if devices have type_id values
        cur.execute('SELECT COUNT(*) FROM devices WHERE type_id IS NOT NULL')
        devices_with_type = cur.fetchone()[0]
        print(f"\nDevices with type_id: {devices_with_type}")
        
        cur.execute('SELECT COUNT(*) FROM devices WHERE type_id IS NULL')
        devices_without_type = cur.fetchone()[0]
        print(f"Devices without type_id: {devices_without_type}")
        
        # Check a few devices to see their type_id values
        cur.execute('SELECT id, name, type_id FROM devices LIMIT 5')
        sample_devices = cur.fetchall()
        print("\nSample devices:")
        for device in sample_devices:
            print(f"  ID: {device[0]}, Name: {device[1]}, Type ID: {device[2]}")
        
        con.close()
        
    except Exception as e:
        print(f"Error checking device types: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_device_types()